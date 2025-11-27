"""
Custom layers for model loading
"""
import keras
from keras import layers
from keras import backend as K


@keras.saving.register_keras_serializable(name="MBConvBlock")
class MBConvBlock(layers.Layer):
    """Mobile Inverted Residual Bottleneck Block (MBConv)"""
    
    def __init__(
        self,
        filters,
        kernel_size=3,
        strides=1,
        expand_ratio=1,
        se_ratio=0.0,
        drop_connect_rate=0.0,
        input_filters=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.filters = filters
        self.kernel_size = kernel_size
        self.strides = strides
        self.expand_ratio = expand_ratio
        self.se_ratio = se_ratio
        self.drop_connect_rate = drop_connect_rate
        self.input_filters = input_filters
    
    def build(self, input_shape):
        inp = input_shape[-1]
        if self.input_filters is None:
            self.input_filters = inp
        
        # Expansion phase
        filters = self.input_filters * self.expand_ratio
        if self.expand_ratio != 1:
            self.expand_conv = layers.Conv2D(
                filters,
                1,
                padding="same",
                use_bias=False,
                name=f"{self.name}_expand_conv"
            )
            self.bn0 = layers.BatchNormalization(name=f"{self.name}_expand_bn")
            self.act0 = layers.Activation("swish", name=f"{self.name}_expand_activation")
        
        # Depthwise conv
        self.dwconv = layers.DepthwiseConv2D(
            self.kernel_size,
            strides=self.strides,
            padding="same",
            use_bias=False,
            name=f"{self.name}_dwconv"
        )
        self.bn1 = layers.BatchNormalization(name=f"{self.name}_bn")
        self.act1 = layers.Activation("swish", name=f"{self.name}_activation")
        
        # Squeeze and excitation
        if 0 < self.se_ratio <= 1:
            se_filters = max(1, int(self.input_filters * self.se_ratio))
            self.se_squeeze = layers.GlobalAveragePooling2D(name=f"{self.name}_se_squeeze")
            self.se_reshape = layers.Reshape((1, 1, filters))
            self.se_reduce = layers.Conv2D(
                se_filters,
                1,
                activation="swish",
                padding="same",
                name=f"{self.name}_se_reduce"
            )
            self.se_expand = layers.Conv2D(
                filters,
                1,
                activation="sigmoid",
                padding="same",
                name=f"{self.name}_se_expand"
            )
            self.se_multiply = layers.Multiply(name=f"{self.name}_se_excite")
        
        # Output phase
        self.project_conv = layers.Conv2D(
            self.filters,
            1,
            padding="same",
            use_bias=False,
            name=f"{self.name}_project_conv"
        )
        self.bn2 = layers.BatchNormalization(name=f"{self.name}_project_bn")
        
        # Skip connection
        if self.strides == 1 and self.input_filters == self.filters:
            if self.drop_connect_rate > 0:
                self.drop = layers.Dropout(
                    self.drop_connect_rate,
                    noise_shape=(None, 1, 1, 1),
                    name=f"{self.name}_drop"
                )
            self.add = layers.Add(name=f"{self.name}_add")
        
        super().build(input_shape)
    
    def call(self, inputs, training=None):
        x = inputs
        
        # Expansion
        if self.expand_ratio != 1:
            x = self.expand_conv(x)
            x = self.bn0(x, training=training)
            x = self.act0(x)
        
        # Depthwise
        x = self.dwconv(x)
        x = self.bn1(x, training=training)
        x = self.act1(x)
        
        # Squeeze and excitation
        if 0 < self.se_ratio <= 1:
            se = self.se_squeeze(x)
            se = self.se_reshape(se)
            se = self.se_reduce(se)
            se = self.se_expand(se)
            x = self.se_multiply([x, se])
        
        # Output
        x = self.project_conv(x)
        x = self.bn2(x, training=training)
        
        # Skip connection
        if self.strides == 1 and self.input_filters == self.filters:
            if self.drop_connect_rate > 0:
                x = self.drop(x, training=training)
            x = self.add([inputs, x])
        
        return x
    
    def get_config(self):
        config = super().get_config()
        config.update({
            "filters": self.filters,
            "kernel_size": self.kernel_size,
            "strides": self.strides,
            "expand_ratio": self.expand_ratio,
            "se_ratio": self.se_ratio,
            "drop_connect_rate": self.drop_connect_rate,
            "input_filters": self.input_filters,
        })
        return config
