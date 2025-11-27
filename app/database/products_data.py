# Comprehensive skincare knowledge base for RAG system
SKINCARE_KNOWLEDGE = """
SKIN DISEASE INFORMATION:

1. ACTINIC KERATOSIS
- Keratosis aktinik adalah pertumbuhan kasar dan bersisik pada kulit akibat paparan sinar matahari berlebihan
- Biasanya muncul di area yang sering terkena sinar matahari seperti wajah, tangan, dan lengan
- Perawatan: Gunakan sunscreen SPF 50+ setiap hari, hindari paparan sinar matahari langsung
- Konsultasikan dengan dokter kulit untuk treatment medis seperti cryotherapy atau krim topikal

2. BASAL CELL CARCINOMA
- Kanker kulit paling umum, biasanya muncul sebagai benjolan mengkilap atau luka yang tidak sembuh
- Disebabkan oleh paparan sinar UV jangka panjang
- Perawatan: Segera konsultasi dengan dokter kulit, mungkin memerlukan pembedahan atau terapi radiasi
- Pencegahan: Gunakan sunscreen broad-spectrum SPF 30+ setiap hari

3. DERMATOFIBROMA
- Benjolan keras jinak pada kulit, biasanya berwarna coklat atau merah
- Tidak berbahaya tetapi bisa terasa gatal atau nyeri jika tertekan
- Perawatan: Umumnya tidak memerlukan treatment, gunakan pelembab untuk menjaga kelembaban kulit
- Jika mengganggu, konsultasi dengan dokter untuk pengangkatan

4. MELANOCYTIC NEVUS (TAHI LALAT)
- Pertumbuhan kulit jinak yang berisi melanosit (sel pigmen)
- Normal memiliki tahi lalat, tetapi perhatikan perubahan bentuk, warna, atau ukuran
- Perawatan: Lindungi dari sinar matahari dengan sunscreen
- Konsultasi dokter jika tahi lalat berubah atau mencurigakan

5. PIGMENTED BENIGN KERATOSIS
- Pertumbuhan kulit jinak berwarna coklat atau hitam
- Umum terjadi seiring bertambahnya usia
- Perawatan: Gunakan produk dengan retinol atau vitamin C untuk mencerahkan kulit
- Sunscreen wajib untuk mencegah hiperpigmentasi

6. SEBORRHEIC KERATOSIS
- Pertumbuhan kulit jinak berwarna coklat, hitam atau kuning
- Terlihat seperti kutil tetapi tidak disebabkan oleh virus
- Perawatan: Tidak memerlukan treatment kecuali mengganggu, gunakan pelembab rutin
- Konsultasi dokter jika ingin diangkat untuk alasan estetika

7. SQUAMOUS CELL CARCINOMA
- Jenis kanker kulit yang berkembang dari sel skuamosa di epidermis
- Muncul sebagai benjolan keras atau luka bersisik yang tidak sembuh
- Perawatan: Segera konsultasi dokter kulit, memerlukan pembedahan atau terapi
- Pencegahan penting: Sunscreen SPF 50+ dan hindari paparan UV

8. VASCULAR LESION
- Kelainan pembuluh darah yang terlihat di kulit seperti hemangioma atau spider veins
- Bisa muncul sebagai bintik merah atau benang merah di kulit
- Perawatan: Gunakan produk yang menenangkan seperti centella atau niacinamide
- Konsultasi dokter untuk laser treatment jika mengganggu

GENERAL SKINCARE TIPS:
- Rutin membersihkan wajah 2x sehari dengan gentle cleanser
- Gunakan pelembab sesuai jenis kulit (oily, dry, combination)
- WAJIB pakai sunscreen SPF 30+ setiap hari, bahkan di dalam ruangan
- Hindari menggaruk atau memencet jerawat
- Minum air putih minimal 8 gelas per hari
- Tidur cukup 7-8 jam per hari
- Kelola stress dengan baik
- Konsumsi makanan bergizi tinggi antioksidan
"""

PRODUCTS = [
    {
        "id": "1",
        "name": "Cetaphil Gentle Skin Cleanser",
        "price": 150000,
        "category": "Pembersih",
        "for_conditions": ["Jerawat", "Kulit Sensitif", "Dermatitis"],
        "description": "Pembersih wajah lembut untuk kulit sensitif dan berjerawat. Formula non-soap, pH balanced, tidak mengandung pewangi. Cocok untuk pembersihan sehari-hari tanpa membuat kulit kering. Dermatologically tested dan hypoallergenic. Dapat digunakan dengan atau tanpa air. Ideal untuk kondisi acne, rosacea, dan post-procedure skin.",
        "ingredients": "Water, Cetyl Alcohol, Propylene Glycol, Sodium Lauryl Sulfate, Stearyl Alcohol",
        "usage": "Aplikasikan ke wajah basah, pijat lembut, bilas dengan air. Gunakan 2x sehari pagi dan malam."
    },
    {
        "id": "2",
        "name": "La Roche-Posay Effaclar Duo+",
        "price": 320000,
        "category": "Perawatan Jerawat",
        "for_conditions": ["Jerawat", "Bekas Jerawat", "Acne Prone Skin"],
        "description": "Treatment anti-jerawat dengan teknologi dual action. Mengandung 5.5% Niacinamide untuk mencerahkan bekas jerawat, Salicylic Acid untuk membersihkan pori, dan Piroctone Olamine sebagai antibakteri. Mengurangi jerawat hingga 50% dalam 4 minggu. Non-comedogenic dan oil-free. Cocok untuk kulit berminyak dan acne-prone.",
        "ingredients": "Niacinamide 5.5%, Salicylic Acid, Piroctone Olamine, La Roche-Posay Thermal Water",
        "usage": "Aplikasikan tipis ke seluruh wajah atau area berjerawat setelah cleansing, hindari area mata. Gunakan 1-2x sehari."
    },
    {
        "id": "3",
        "name": "Avene Thermal Spring Water",
        "price": 180000,
        "category": "Spray Thermal",
        "for_conditions": ["Kulit Sensitif", "Dermatitis", "Rosacea", "Sunburn"],
        "description": "Spray air thermal murni dari sumber Avene, Perancis. Mengandung mineral dan trace elements yang menenangkan kulit. Soothing, anti-inflammatory, dan mengurangi kemerahan. Steril dan bebas preservatives. Cocok untuk kulit sensitif, iritasi, sunburn, dan post-procedure. Dapat digunakan sebagai setting spray atau refresh skin.",
        "ingredients": "Avene Thermal Spring Water 100%",
        "usage": "Semprot ke wajah dari jarak 20cm, biarkan meresap 1-2 menit, tepuk lembut kelebihan air. Gunakan kapan saja."
    },
    {
        "id": "4",
        "name": "Wardah Nature Daily Aloe Vera Gel",
        "price": 25000,
        "category": "Pelembab",
        "for_conditions": ["Kulit Kering", "Luka Bakar Ringan", "Sunburn", "Iritasi"],
        "description": "Gel aloe vera murni 100% untuk melembabkan dan menenangkan kulit. Tekstur ringan, cepat menyerap, tidak lengket. Mengandung vitamin A, C, E untuk nutrisi kulit. Multi-fungsi: pelembab wajah, body lotion, hair mask, atau after-sun care. Hypoallergenic dan cocok untuk semua jenis kulit. Produk lokal berkualitas dengan harga terjangkau.",
        "ingredients": "Aloe Barbadensis Leaf Extract 100%, Vitamin A, C, E",
        "usage": "Aplikasikan secukupnya ke area yang diinginkan. Untuk wajah gunakan tipis-tipis. Dapat digunakan 2-3x sehari."
    },
    {
        "id": "5",
        "name": "Somethinc Calm Down Centella Serum",
        "price": 89000,
        "category": "Serum",
        "for_conditions": ["Jerawat", "Kulit Sensitif", "Kemerahan", "Barrier Rusak"],
        "description": "Serum dengan 100,000ppm Centella Asiatica untuk menenangkan kulit. Mengandung Madecassoside, Asiaticoside, Madecassic Acid untuk repair skin barrier. Plus 10% Niacinamide untuk brighten dan control sebum. Hypoallergenic, fragrance-free, alcohol-free. Cocok untuk acne-prone, sensitive skin, dan rosacea. Produk lokal dengan formula setara brand internasional.",
        "ingredients": "Centella Asiatica 100,000ppm, Niacinamide 10%, Madecassoside, Asiaticoside",
        "usage": "Aplikasikan 2-3 tetes ke wajah setelah toner, sebelum moisturizer. Gunakan pagi dan malam. Dapat dicampur dengan moisturizer."
    },
    {
        "id": "6",
        "name": "Bioderma Atoderm Cream",
        "price": 250000,
        "category": "Pelembab Intensif",
        "for_conditions": ["Eksim", "Dermatitis", "Kulit Sangat Kering", "Psoriasis"],
        "description": "Pelembab intensive untuk kondisi kulit sangat kering, eksim, dan dermatitis. Formula Skin Barrier Therapy dengan Lipigenium complex untuk restore lipid barrier. Mengandung Niacinamide dan Vitamin PP untuk anti-inflammatory. Tekstur rich dan creamy, melembabkan hingga 24 jam. Hypoallergenic, fragrance-free, dan non-comedogenic. Cocok untuk bayi, anak, dan dewasa.",
        "ingredients": "Lipigenium Complex, Niacinamide, Vitamin PP, Glycerin, Shea Butter",
        "usage": "Aplikasikan ke kulit bersih 1-2x sehari. Untuk area sangat kering aplikasikan lebih sering. Gunakan setelah mandi."
    },
    {
        "id": "7",
        "name": "Emina Sun Protection SPF 30 PA+++",
        "price": 35000,
        "category": "Sunscreen",
        "for_conditions": ["Semua Jenis Kulit", "Daily Protection"],
        "description": "Sunscreen broad-spectrum dengan SPF 30 PA+++ untuk perlindungan dari UVA dan UVB. Formula ringan, tidak lengket, cepat menyerap. Tidak meninggalkan whitecast. Water-resistant dan cocok sebagai base makeup. Non-comedogenic, oil-free, fragrance-free. Harga sangat terjangkau untuk penggunaan sehari-hari. Reapply setiap 2-3 jam untuk perlindungan optimal.",
        "ingredients": "Ethylhexyl Methoxycinnamate, Titanium Dioxide, Zinc Oxide, Vitamin E",
        "usage": "Aplikasikan sebagai step terakhir skincare 15 menit sebelum keluar rumah. Gunakan 2 jari amount untuk wajah dan leher. Reapply tiap 2-3 jam."
    },
    {
        "id": "8",
        "name": "Physiogel Daily Moisture Therapy",
        "price": 220000,
        "category": "Pelembab",
        "for_conditions": ["Kulit Kering", "Dermatitis", "Kulit Sensitif", "Barrier Rusak"],
        "description": "Pelembab dengan teknologi BioMimic untuk meniru lipid barrier alami kulit. Mengandung ceramides dan lipids untuk strengthen skin barrier. Hypoallergenic, fragrance-free, paraben-free, dan non-comedogenic. Clinically proven untuk kulit kering dan sensitif. Tekstur ringan tetapi moisturizing. Cocok untuk daily use dan dapat digunakan untuk bayi hingga dewasa.",
        "ingredients": "BioMimic Technology, Ceramides, Lipids, Glycerin, Dimethicone",
        "usage": "Aplikasikan ke wajah dan tubuh setelah cleansing. Gunakan 2x sehari pagi dan malam. Dapat digunakan sebelum sunscreen."
    },
    {
        "id": "9",
        "name": "Skintific 5X Ceramide Barrier Repair Moisturizer",
        "price": 135000,
        "category": "Pelembab",
        "for_conditions": ["Barrier Rusak", "Kulit Sensitif", "Kulit Kering"],
        "description": "Moisturizer dengan 5X Ceramide complex untuk intensive barrier repair. Mengandung 5% Niacinamide untuk brighten dan control sebum. Formula lightweight gel-cream yang cepat menyerap. Hypoallergenic, fragrance-free, dan alcohol-free. Cocok untuk semua jenis kulit terutama dehydrated dan sensitive skin. Produk lokal dengan teknologi Korea.",
        "ingredients": "5X Ceramide Complex, Niacinamide 5%, Hyaluronic Acid, Centella Asiatica",
        "usage": "Aplikasikan sebagai step terakhir skincare pagi dan malam. Untuk kulit sangat kering, layer 2-3x hingga fully absorbed."
    },
    {
        "id": "10",
        "name": "Azarine Hydrasoothe Sunscreen Gel SPF 45",
        "price": 55000,
        "category": "Sunscreen",
        "for_conditions": ["Semua Jenis Kulit", "Kulit Berminyak", "Acne Prone"],
        "description": "Sunscreen gel dengan SPF 45 PA++++ untuk maximum protection. Formula gel yang ultra-light, matte finish, tidak lengket. Mengandung Hyaluronic Acid dan Centella Asiatica untuk hydrate dan soothe. Tidak ada whitecast sama sekali. Cocok untuk kulit berminyak dan acne-prone. Water and sweat resistant. Harga affordable untuk pemakaian generous.",
        "ingredients": "Ethylhexyl Methoxycinnamate, Titanium Dioxide, Hyaluronic Acid, Centella Asiatica",
        "usage": "Aplikasikan generous amount (2 jari) ke wajah 15 menit sebelum aktivitas outdoor. Reapply setiap 2 jam atau setelah berkeringat."
    },
    {
        "id": "11",
        "name": "Cosrx Advanced Snail 96 Mucin Power Essence",
        "price": 185000,
        "category": "Serum",
        "for_conditions": ["Kulit Kering", "Bekas Jerawat", "Anti Aging"],
        "description": "Essence dengan 96% Snail Secretion Filtrate untuk intense hydration dan skin repair. Mempercepat penyembuhan bekas jerawat, mengurangi fine lines, dan meningkatkan skin elasticity. Tekstur lightweight gel yang mudah menyerap. Hypoallergenic dan dermatologically tested. Cocok untuk semua jenis kulit.",
        "ingredients": "Snail Secretion Filtrate 96%, Betaine, Panthenol, Arginine",
        "usage": "Setelah toner, aplikasikan 2-3 tetes ke wajah, tap lembut. Gunakan pagi dan malam."
    },
    {
        "id": "12",
        "name": "Some By Mi AHA BHA PHA 30 Days Miracle Toner",
        "price": 145000,
        "category": "Toner",
        "for_conditions": ["Jerawat", "Komedo", "Kulit Kusam"],
        "description": "Toner eksfoliasi dengan AHA, BHA, dan PHA untuk deep cleansing pori-pori. Mengandung 10,000ppm Tea Tree untuk anti-bakteri. Mengurangi jerawat, komedo, dan mencerahkan kulit dalam 30 hari. pH balanced dan tidak membuat kulit kering.",
        "ingredients": "Tea Tree 10,000ppm, AHA, BHA, PHA, Niacinamide, Adenosine",
        "usage": "Setelah cleansing, tuang ke kapas atau telapak tangan, tap ke wajah. Gunakan 1-2x sehari. Wajib pakai sunscreen."
    },
    {
        "id": "13",
        "name": "Innisfree Green Tea Seed Serum",
        "price": 195000,
        "category": "Serum",
        "for_conditions": ["Kulit Kering", "Dehidrasi", "Kulit Kusam"],
        "description": "Serum dengan Fresh Green Tea Tri-biotics untuk deep hydration. Mengandung Green Tea Extract dari Jeju Island. Menyeimbangkan kelembaban kulit, memperkuat skin barrier, dan memberikan glow natural. Formula lightweight yang cepat menyerap.",
        "ingredients": "Green Tea Extract, Green Tea Seed Oil, Hyaluronic Acid, Panthenol",
        "usage": "Aplikasikan 2-3 pump setelah toner. Tap lembut hingga menyerap. Gunakan pagi dan malam."
    },
    {
        "id": "14",
        "name": "The Ordinary Hyaluronic Acid 2% + B5",
        "price": 95000,
        "category": "Serum",
        "for_conditions": ["Kulit Kering", "Dehidrasi", "Fine Lines"],
        "description": "Serum hydrating dengan Hyaluronic Acid multi-molecular weight untuk penetrasi berbagai layer kulit. Vitamin B5 meningkatkan surface hydration. Plumping effect untuk mengurangi fine lines. Water-based formula, lightweight, dan cocok untuk layering.",
        "ingredients": "Hyaluronic Acid 2%, Vitamin B5, Sodium Hyaluronate Crosspolymer",
        "usage": "Aplikasikan beberapa tetes ke wajah basah setelah cleansing. Lanjutkan dengan moisturizer. Gunakan AM dan PM."
    },
    {
        "id": "15",
        "name": "Hada Labo Gokujyun Premium Hyaluronic Lotion",
        "price": 125000,
        "category": "Toner",
        "for_conditions": ["Kulit Kering", "Dehidrasi", "Semua Jenis Kulit"],
        "description": "Hydrating lotion dengan 7 jenis Hyaluronic Acid untuk maximum moisture retention. Tekstur thick tetapi cepat menyerap. Fragrance-free, colorant-free, dan mineral oil-free. Meningkatkan kelembaban kulit hingga 5x lipat. Ideal untuk 7-skin method.",
        "ingredients": "7 Types Hyaluronic Acid, Urea, Sacran, Squalane",
        "usage": "Setelah cleansing, tuang ke telapak tangan, pat ke wajah. Dapat dilayer 2-3x untuk extra hydration."
    },
    {
        "id": "16",
        "name": "Paula's Choice 2% BHA Liquid Exfoliant",
        "price": 385000,
        "category": "Exfoliant",
        "for_conditions": ["Jerawat", "Komedo", "Pori Besar", "Kulit Berminyak"],
        "description": "Leave-on exfoliant dengan 2% Salicylic Acid untuk unclog pores dan mengurangi komedo. Memperbaiki tekstur kulit, mengurangi fine lines, dan mengontrol sebum. Gentle formula non-abrasive. Best-seller worldwide untuk acne-prone skin.",
        "ingredients": "Salicylic Acid 2%, Green Tea Extract, Methylpropanediol",
        "usage": "Setelah cleansing dan toner, aplikasikan dengan kapas atau tangan. Tidak perlu dibilas. Mulai 2-3x seminggu, bisa ditingkatkan. Wajib sunscreen."
    },
    {
        "id": "17",
        "name": "Kiehl's Ultra Facial Cream",
        "price": 425000,
        "category": "Pelembab",
        "for_conditions": ["Kulit Kering", "Kulit Sensitif", "Semua Jenis Kulit"],
        "description": "Lightweight moisturizer dengan 24-hour hydration. Mengandung Squalane dan Glacial Glycoprotein untuk strengthen skin barrier. Suitable untuk extreme weather conditions. Non-greasy, fragrance-free, dan cocok untuk semua jenis kulit termasuk sensitif.",
        "ingredients": "Squalane, Glacial Glycoprotein, Imperata Cylindrica Root Extract",
        "usage": "Aplikasikan ke wajah dan leher setelah serum. Gunakan pagi dan malam. Dapat digunakan di bawah makeup."
    },
    {
        "id": "18",
        "name": "Dear Klairs Freshly Juiced Vitamin Drop",
        "price": 245000,
        "category": "Serum",
        "for_conditions": ["Kulit Kusam", "Hiperpigmentasi", "Bekas Jerawat"],
        "description": "Vitamin C serum dengan 5% pure Ascorbic Acid untuk brightening dan anti-aging. Gentle formula cocok untuk sensitive skin. Mengurangi dark spots, meratakan skin tone, dan meningkatkan radiance. Essential oil-free dan hypoallergenic.",
        "ingredients": "Ascorbic Acid 5%, Centella Asiatica, Licorice Root Extract",
        "usage": "Gunakan 3-4 tetes setelah toner, sebelum moisturizer. Mulai 2x seminggu, tingkatkan bertahap. Gunakan PM atau dengan sunscreen di AM."
    },
    {
        "id": "19",
        "name": "Acnes Natural Care Foaming Wash",
        "price": 28000,
        "category": "Pembersih",
        "for_conditions": ["Jerawat", "Kulit Berminyak", "Komedo"],
        "description": "Facial wash dengan Isopropyl Methylphenol untuk anti-bakteri dan mencegah jerawat. Vitamin B3 dan Aloe Vera menenangkan kulit. Formula foam yang lembut membersihkan excess oil tanpa membuat kulit kering. pH balanced.",
        "ingredients": "Isopropyl Methylphenol, Vitamin B3, Aloe Vera, Glycerin",
        "usage": "Basahi wajah, buat busa, pijat lembut, bilas. Gunakan 2x sehari pagi dan malam."
    },
    {
        "id": "20",
        "name": "Senka Perfect Whip",
        "price": 42000,
        "category": "Pembersih",
        "for_conditions": ["Semua Jenis Kulit", "Kulit Berminyak"],
        "description": "Japanese facial foam dengan micro-bubble technology untuk deep cleansing. White Cocoon Extract mencerahkan dan menghaluskan kulit. Rich foam yang lembut mengangkat kotoran tanpa stripping. Cocok untuk daily use.",
        "ingredients": "White Cocoon Extract, Hyaluronic Acid, Collagen, Silk Protein",
        "usage": "Keluarkan 2cm, buat busa dengan air, aplikasikan ke wajah, pijat, bilas. Gunakan 2x sehari."
    },
    {
        "id": "21",
        "name": "Nivea Creme Soft Soap",
        "price": 18000,
        "category": "Pembersih",
        "for_conditions": ["Kulit Kering", "Kulit Normal"],
        "description": "Sabun wajah dan tubuh dengan Moisturizing Cream untuk cleansing tanpa membuat kulit kering. Cocok untuk sensitive skin. Memberikan soft dan smooth feeling setelah pemakaian. Affordable untuk whole family.",
        "ingredients": "Moisturizing Cream, Vitamin E, Glycerin",
        "usage": "Basahi kulit, buat busa dengan sabun, aplikasikan, bilas. Gunakan setiap mandi."
    },
    {
        "id": "22",
        "name": "Garnier Micellar Cleansing Water",
        "price": 35000,
        "category": "Pembersih",
        "for_conditions": ["Semua Jenis Kulit", "Kulit Sensitif"],
        "description": "Micellar water all-in-one: cleanser, makeup remover, dan toner. Micelle technology mengangkat makeup dan impurities tanpa harsh rubbing. No-rinse formula. Alcohol-free, fragrance-free, dan cocok untuk sensitive skin.",
        "ingredients": "Micelle Technology, Glycerin, Poloxamer 184",
        "usage": "Tuang ke kapas, usap lembut ke wajah hingga bersih. Tidak perlu dibilas. Gunakan pagi dan/atau malam."
    },
    {
        "id": "23",
        "name": "The Body Shop Tea Tree Skin Clearing Facial Wash",
        "price": 145000,
        "category": "Pembersih",
        "for_conditions": ["Jerawat", "Kulit Berminyak", "Komedo"],
        "description": "Gel cleanser dengan Community Fair Trade Tea Tree Oil untuk deep cleansing dan anti-blemish. Lemon Tea Tree dan Tamanu Oil menenangkan kulit. Mengurangi excess oil dan mencegah jerawat. Vegan dan cruelty-free.",
        "ingredients": "Tea Tree Oil, Lemon Tea Tree, Tamanu Oil, Salicylic Acid",
        "usage": "Aplikasikan ke wajah basah, massage, bilas. Gunakan AM dan PM. Hindari area mata."
    },
    {
        "id": "24",
        "name": "Neutrogena Hydro Boost Water Gel",
        "price": 265000,
        "category": "Pelembab",
        "for_conditions": ["Kulit Kering", "Dehidrasi", "Kulit Berminyak"],
        "description": "Gel-cream dengan Hyaluronic Acid untuk boost hydration. Unique water gel formula yang instantly hydrates dan menyerap cepat. Oil-free dan non-comedogenic. Locks in moisture selama 48 jam. Suitable untuk oily dan acne-prone skin.",
        "ingredients": "Hyaluronic Acid, Glycerin, Dimethicone, Olive Extract",
        "usage": "Aplikasikan ke wajah bersih pagi dan malam. Dapat digunakan setelah serum atau standalone."
    },
    {
        "id": "25",
        "name": "Laneige Water Sleeping Mask",
        "price": 315000,
        "category": "Masker",
        "for_conditions": ["Kulit Kering", "Kulit Kusam", "Dehidrasi"],
        "description": "Overnight mask dengan Sleep-tox technology untuk intensive hydration. Hunza Apricot dan Evening Primrose melembabkan dan mencerahkan kulit overnight. Bangun dengan glowing, plump skin. K-beauty essential.",
        "ingredients": "Hunza Apricot, Evening Primrose, Sleepscent, Hydro Ion Mineral Water",
        "usage": "Gunakan sebagai step terakhir skincare malam. Aplikasikan layer tebal, biarkan overnight, bilas pagi. 2-3x seminggu."
    },
    {
        "id": "26",
        "name": "Pixi Glow Tonic",
        "price": 275000,
        "category": "Toner",
        "for_conditions": ["Kulit Kusam", "Pori Besar", "Tekstur Kasar"],
        "description": "Exfoliating toner dengan 5% Glycolic Acid untuk gentle daily exfoliation. Ginseng dan Aloe Vera soothe dan tone skin. Memberikan radiant glow. Cult favorite untuk achieving glass skin. Alcohol-free.",
        "ingredients": "Glycolic Acid 5%, Ginseng, Aloe Vera, Horse Chestnut",
        "usage": "Setelah cleansing, swipe dengan kapas ke wajah. Tidak perlu dibilas. Gunakan AM atau PM. Wajib sunscreen."
    },
    {
        "id": "27",
        "name": "Bioré UV Aqua Rich Watery Essence SPF 50+",
        "price": 115000,
        "category": "Sunscreen",
        "for_conditions": ["Semua Jenis Kulit", "Kulit Berminyak"],
        "description": "Sunscreen dengan tekstur watery yang super light. SPF 50+ PA++++ untuk maximum protection. Water capsule technology memberikan fresh feeling. Water and sweat resistant. No whitecast. Best-selling Japanese sunscreen worldwide.",
        "ingredients": "Aqua Booster, Hyaluronic Acid, Royal Jelly, Citrus Extracts",
        "usage": "Shake well, aplikasikan generous amount ke wajah 15 menit sebelum sun exposure. Reapply tiap 2-3 jam."
    },
    {
        "id": "28",
        "name": "Innisfree Pore Clearing Clay Mask",
        "price": 145000,
        "category": "Masker",
        "for_conditions": ["Komedo", "Pori Besar", "Kulit Berminyak"],
        "description": "Clay mask dengan Jeju Volcanic Clusters untuk deep pore cleansing. Absorbs excess sebum dan impurities. AHA untuk gentle exfoliation. Skin tone menjadi lebih smooth dan refined. Suitable untuk oily dan combination skin.",
        "ingredients": "Jeju Volcanic Clusters, AHA, Walnut Shell Powder",
        "usage": "Aplikasikan layer tebal ke wajah kering, hindari mata dan bibir. Biarkan 10-15 menit, bilas. Gunakan 1-2x seminggu."
    },
    {
        "id": "29",
        "name": "Klairs Supple Preparation Facial Toner",
        "price": 235000,
        "category": "Toner",
        "for_conditions": ["Kulit Sensitif", "Kulit Kering", "Barrier Rusak"],
        "description": "Hydrating toner dengan essential ingredients untuk prep kulit. Centella, Licorice, dan Beta-Glucan menenangkan dan strengthen skin barrier. pH balanced dan alcohol-free. Suitable untuk 7-skin method. Vegan dan cruelty-free.",
        "ingredients": "Centella Asiatica, Licorice Root, Beta-Glucan, Hyaluronic Acid",
        "usage": "Tuang ke telapak tangan atau kapas, pat ke wajah. Dapat dilayer 2-3x. Gunakan AM dan PM."
    },
    {
        "id": "30",
        "name": "Axis-Y Dark Spot Correcting Glow Serum",
        "price": 185000,
        "category": "Serum",
        "for_conditions": ["Hiperpigmentasi", "Bekas Jerawat", "Kulit Kusam"],
        "description": "Brightening serum dengan 5% Niacinamide, Papaya Extract, dan Squalane. Mengurangi dark spots dan hyperpigmentation. Rice Bran Extract memberikan natural glow. Vegan, cruelty-free, dan fragrance-free.",
        "ingredients": "Niacinamide 5%, Papaya Extract, Rice Bran Extract, Squalane",
        "usage": "Aplikasikan 2-3 tetes setelah toner. Pat lembut. Gunakan pagi dan malam. Cocok untuk morning routine."
    },
    {
        "id": "31",
        "name": "Rohto Hada Labo Shirojyun Premium Whitening Lotion",
        "price": 145000,
        "category": "Toner",
        "for_conditions": ["Hiperpigmentasi", "Kulit Kusam", "Flek Hitam"],
        "description": "Whitening lotion dengan Tranexamic Acid dan Vitamin C derivative untuk mencerahkan kulit. 2 jenis Hyaluronic Acid untuk hydration. Mengurangi dark spots dan meratakan skin tone. Made in Japan dengan teknologi advanced.",
        "ingredients": "Tranexamic Acid, Vitamin C Derivative, Hyaluronic Acid, Vitamin E",
        "usage": "Setelah cleansing, aplikasikan ke seluruh wajah. Dapat dilayer 2-3x untuk extra hydration."
    },
    {
        "id": "32",
        "name": "Melano CC Intensive Anti-Spot Essence",
        "price": 165000,
        "category": "Serum",
        "for_conditions": ["Hiperpigmentasi", "Bekas Jerawat", "Flek Hitam"],
        "description": "Essence dengan pure Vitamin C dan Vitamin E untuk intensive spot treatment. Mencegah dan mengurangi dark spots. Texture lightweight yang cepat menyerap. Best-seller dari Jepang untuk brightening.",
        "ingredients": "Pure Vitamin C, Vitamin E, Isopropyl Methylphenol, Dipotassium Glycyrrhizate",
        "usage": "Aplikasikan langsung ke dark spots atau seluruh wajah setelah toner. Gunakan AM dan PM dengan sunscreen."
    },
    {
        "id": "33",
        "name": "Kose Sekkisei Lotion",
        "price": 385000,
        "category": "Toner",
        "for_conditions": ["Kulit Kusam", "Hiperpigmentasi", "Kulit Kering"],
        "description": "Iconic Japanese lotion dengan Oriental Herbal Complex untuk brightening. Job's Tears, Angelica, dan Melothria untuk mencerahkan dan melembabkan. Cult favorite untuk achieving translucent skin.",
        "ingredients": "Job's Tears Extract, Angelica Extract, Melothria Extract, Alcohol",
        "usage": "Tuang ke kapas, swipe ke wajah dengan gentle upward motion. Dapat digunakan sebagai lotion mask."
    },
    {
        "id": "34",
        "name": "Anessa Perfect UV Sunscreen Skincare Milk SPF 50+",
        "price": 295000,
        "category": "Sunscreen",
        "for_conditions": ["Semua Jenis Kulit", "Outdoor Activity"],
        "description": "Premium Japanese sunscreen dengan Auto Booster Technology yang makin kuat saat terkena keringat dan air. SPF 50+ PA++++ maximum protection. Skincare ingredients untuk merawat kulit. Super waterproof.",
        "ingredients": "Auto Booster Technology, Hyaluronic Acid, Collagen, Green Tea Extract",
        "usage": "Shake well, aplikasikan sebagai step terakhir skincare. Reapply setiap 2-3 jam saat outdoor."
    },
    {
        "id": "35",
        "name": "Shiseido Senka Aging Care UV Sunscreen SPF 50+",
        "price": 78000,
        "category": "Sunscreen",
        "for_conditions": ["Anti Aging", "Kulit Kering", "Daily Protection"],
        "description": "Sunscreen dengan anti-aging benefits. WR Collagen EX dan WR Hyaluronic Acid untuk melembabkan dan mencegah aging. Texture ringan, no whitecast. Water resistant dan affordable untuk daily use.",
        "ingredients": "WR Collagen EX, WR Hyaluronic Acid, Vitamin E, UV Filters",
        "usage": "Aplikasikan generous amount ke wajah dan leher. Reapply tiap 2-3 jam untuk optimal protection."
    },
    {
        "id": "36",
        "name": "Kanebo Suisai Beauty Clear Powder",
        "price": 175000,
        "category": "Pembersih",
        "for_conditions": ["Komedo", "Pori Besar", "Kulit Kusam"],
        "description": "Enzyme powder wash dengan 2 enzymes (Protease dan Lipase) untuk deep cleansing. Removes blackheads, excess sebum, dan dead skin cells. Individual capsule untuk freshness. Made in Japan.",
        "ingredients": "Protease, Lipase, Amino Acid, Hyaluronic Acid",
        "usage": "Basahi tangan, buka 1 kapsul, tambah air, buat busa, massage wajah, bilas. Gunakan 1-2x seminggu."
    },
    {
        "id": "37",
        "name": "DHC Deep Cleansing Oil",
        "price": 245000,
        "category": "Pembersih",
        "for_conditions": ["Semua Jenis Kulit", "Makeup Removal"],
        "description": "Best-selling cleansing oil dari Jepang dengan Olive Oil. Melts away makeup, sunscreen, dan impurities tanpa stripping. Water-soluble dan rinses clean. Suitable untuk semua jenis kulit including sensitive.",
        "ingredients": "Olive Oil, Vitamin E, Rosemary Extract",
        "usage": "Aplikasikan ke wajah kering, massage, tambah air untuk emulsify, bilas. Double cleanse recommended."
    },
    {
        "id": "38",
        "name": "Rohto Mentholatum Acnes Creamy Wash",
        "price": 32000,
        "category": "Pembersih",
        "for_conditions": ["Jerawat", "Kulit Berminyak", "Komedo"],
        "description": "Medicated facial wash dengan Isopropyl Methylphenol untuk anti-bakteri. Vitamin B6 dan E untuk skin health. Creamy foam yang gentle namun effective untuk acne-prone skin.",
        "ingredients": "Isopropyl Methylphenol, Vitamin B6, Vitamin E, Glycerin",
        "usage": "Keluarkan 2-3cm, buat busa, aplikasikan ke wajah, massage, bilas. Gunakan AM dan PM."
    },
    {
        "id": "39",
        "name": "Shiseido Elixir Superieur Lifting Moisture Lotion",
        "price": 425000,
        "category": "Toner",
        "for_conditions": ["Anti Aging", "Kulit Kering", "Loss of Elasticity"],
        "description": "Premium anti-aging lotion dengan Collagen GL dan Age Defense Complex. Improves skin elasticity dan firmness. Deeply hydrates dan prepares skin untuk better absorption. Luxury Japanese skincare.",
        "ingredients": "Collagen GL, Age Defense Complex, Hyaluronic Acid, Aqua Collagen",
        "usage": "Setelah cleansing, tuang ke kapas atau telapak tangan, pat ke wajah dan leher. Gunakan AM dan PM."
    },
    {
        "id": "40",
        "name": "Naturie Hatomugi Skin Conditioning Gel",
        "price": 95000,
        "category": "Pelembab",
        "for_conditions": ["Semua Jenis Kulit", "Kulit Dehidrasi"],
        "description": "All-in-one gel dengan Job's Tears (Hatomugi) Extract. Lightweight gel texture yang instantly hydrates. Can be used as toner, serum, moisturizer, atau mask. Large size 180g sangat economical.",
        "ingredients": "Hatomugi (Job's Tears) Extract, Hyaluronic Acid, Placenta Extract",
        "usage": "Aplikasikan generous amount ke wajah dan tubuh. Dapat digunakan sebagai sleeping mask dengan layer tebal."
    },
    {
        "id": "41",
        "name": "Kikumasamune High Moist Lotion",
        "price": 115000,
        "category": "Toner",
        "for_conditions": ["Kulit Kering", "Kulit Kusam", "Body Care"],
        "description": "Sake lotion dengan Rice Ferment Filtrate untuk brightening dan hydration. Amino acids dan ceramides untuk strengthen barrier. Huge 500ml bottle untuk face dan body. Pink bottle cult favorite.",
        "ingredients": "Sake (Rice Ferment), Arbutin, Placenta Extract, Ceramides, Amino Acids",
        "usage": "Tuang generous amount ke tangan atau spray bottle, aplikasikan ke wajah dan body. Layer multiple times."
    },
    {
        "id": "42",
        "name": "Rohto Obagi C20 Serum",
        "price": 385000,
        "category": "Serum",
        "for_conditions": ["Hiperpigmentasi", "Kulit Kusam", "Anti Aging"],
        "description": "High concentration Vitamin C serum dengan 20% pure L-Ascorbic Acid. Powerful brightening dan anti-aging. Vitamin E untuk stability. Premium Japanese formula untuk visible results.",
        "ingredients": "Vitamin C 20% (L-Ascorbic Acid), Vitamin E, Propylene Glycol",
        "usage": "Aplikasikan 3-4 tetes ke wajah setelah toner. Gunakan PM only atau dengan sunscreen di AM. Store in cool place."
    },
    {
        "id": "43",
        "name": "Curel Intensive Moisture Care Emulsion",
        "price": 245000,
        "category": "Pelembab",
        "for_conditions": ["Kulit Sensitif", "Kulit Kering", "Dermatitis"],
        "description": "Emulsion untuk sensitive dry skin dengan Ceramide functional ingredients. Fragrance-free, colorant-free, alcohol-free. Hypoallergenic dan dermatologically tested. Strengthens skin barrier dan deeply moisturizes.",
        "ingredients": "Ceramide Functional Ingredients, Eucalyptus Extract, Glycerin",
        "usage": "Setelah lotion/toner, aplikasikan ke wajah dengan gentle pressing motion. Gunakan AM dan PM."
    },
    {
        "id": "44",
        "name": "Softymo Speedy Cleansing Oil",
        "price": 85000,
        "category": "Pembersih",
        "for_conditions": ["Semua Jenis Kulit", "Makeup Removal"],
        "description": "Fast-acting cleansing oil yang removes makeup dalam 10 detik. 5 organic oils untuk nourishment. Rinses clean tanpa residue. Affordable Japanese makeup remover untuk daily use.",
        "ingredients": "Organic Oils (Jojoba, Olive, Sesame, Shea, Safflower)",
        "usage": "Aplikasikan ke wajah kering, massage 10 detik, tambah air, emulsify, bilas."
    },
    {
        "id": "45",
        "name": "Minon Amino Moist Charge Milk",
        "price": 265000,
        "category": "Pelembab",
        "for_conditions": ["Kulit Sensitif", "Kulit Kering", "Barrier Rusak"],
        "description": "Milky lotion dengan 9 Amino Acids untuk repair dan strengthen barrier. Untuk sensitive skin yang mudah iritasi. Fragrance-free dan hypoallergenic. Provides long-lasting moisture tanpa heaviness.",
        "ingredients": "9 Amino Acids Complex, Ceramide, Hyaluronic Acid",
        "usage": "Setelah toner, pump 1-2x ke telapak tangan, aplikasikan ke seluruh wajah. Gunakan AM dan PM."
    },
    {
        "id": "46",
        "name": "Kracie Naive Deep Cleansing Oil",
        "price": 68000,
        "category": "Pembersih",
        "for_conditions": ["Semua Jenis Kulit", "Komedo"],
        "description": "Affordable cleansing oil dengan Grape Seed Oil. Deep cleansing untuk blackheads dan makeup. Light texture yang easy to rinse. Budget-friendly Japanese quality.",
        "ingredients": "Grape Seed Oil, Olive Oil, Vitamin E",
        "usage": "Massage ke wajah kering, fokus ke area berminyak, emulsify dengan air, bilas thoroughly."
    },
    {
        "id": "47",
        "name": "Sana Nameraka Honpo Soy Milk Isoflavone Lotion",
        "price": 105000,
        "category": "Toner",
        "for_conditions": ["Anti Aging", "Kulit Kering", "Loss of Firmness"],
        "description": "Soy milk lotion dengan Isoflavones untuk anti-aging. Improves skin elasticity dan firmness. Hyaluronic Acid untuk moisture. Affordable anti-aging option dari Jepang.",
        "ingredients": "Soy Milk Extract, Isoflavones, Hyaluronic Acid, Collagen",
        "usage": "Tuang ke telapak tangan, pat ke wajah hingga absorbed. Dapat dilayer untuk extra moisture."
    },
    {
        "id": "48",
        "name": "Orbis Clear Full Wash",
        "price": 125000,
        "category": "Pembersih",
        "for_conditions": ["Jerawat", "Kulit Berminyak", "Pori Besar"],
        "description": "Facial wash khusus acne-prone skin dengan Amino Acid base. Gentle cleansing tanpa stripping. Mencegah breakouts dan controls sebum. Oil-free dan non-comedogenic.",
        "ingredients": "Amino Acids, Dipotassium Glycyrrhizate, Collagen, Purple Brasilian Clay",
        "usage": "Buat rich foam, massage ke wajah dengan circular motion, bilas. Gunakan 2x sehari."
    },
    {
        "id": "49",
        "name": "Utena Puresa Golden Jelly Mask Hyaluronic Acid",
        "price": 45000,
        "category": "Masker",
        "for_conditions": ["Kulit Kering", "Kulit Dehidrasi", "Anti Aging"],
        "description": "Jelly mask dengan Golden Jelly technology untuk intensive hydration. 3 types Hyaluronic Acid untuk multi-layer moisture. Jelly texture yang fit perfectly ke wajah. 3 sheets per pack.",
        "ingredients": "Golden Jelly, Hyaluronic Acid (3 types), Collagen, Placenta",
        "usage": "Aplikasikan ke wajah bersih, biarkan 10-15 menit, remove mask, pat essence. Gunakan 2-3x seminggu."
    },
    {
        "id": "50",
        "name": "Transino Whitening Clear Lotion",
        "price": 335000,
        "category": "Toner",
        "for_conditions": ["Melasma", "Hiperpigmentasi", "Flek Hitam"],
        "description": "Medicated lotion khusus melasma dengan Tranexamic Acid. Intensive whitening untuk stubborn pigmentation. Dipotassium Glycyrrhizate untuk anti-inflammatory. Premium Japanese medicated skincare.",
        "ingredients": "Tranexamic Acid, Dipotassium Glycyrrhizate, Vitamin C Derivative",
        "usage": "Setelah cleansing, aplikasikan dengan kapas ke seluruh wajah atau fokus ke dark spots. Gunakan AM dan PM."
    },
    {
        "id": "51",
        "name": "Rosette Ceramide Gel",
        "price": 145000,
        "category": "Pelembab",
        "for_conditions": ["Barrier Rusak", "Kulit Sensitif", "Kulit Kering"],
        "description": "All-in-one gel dengan 3 types Ceramides untuk barrier repair. 5-in-1: toner, essence, emulsion, cream, dan pack. Fragrance-free dan colorant-free. Economical 80g tube.",
        "ingredients": "Ceramide 1, Ceramide 3, Ceramide 6 II, Hyaluronic Acid, Collagen",
        "usage": "Setelah cleansing, aplikasikan ke seluruh wajah. Dapat digunakan solo atau sebelum moisturizer."
    },
    {
        "id": "52",
        "name": "Tsururi Point Clay Pack",
        "price": 95000,
        "category": "Masker",
        "for_conditions": ["Komedo", "Pori Besar", "Hidung Berminyak"],
        "description": "Clay pack khusus untuk nose area. Ghassoul Clay dan Moroccan Lava Clay untuk absorb blackheads. Removes stubborn sebum plugs. AHA untuk gentle exfoliation. Peel-off type.",
        "ingredients": "Ghassoul Clay, Moroccan Lava Clay, AHA, Charcoal Powder",
        "usage": "Aplikasikan thick layer ke hidung atau T-zone, tunggu hingga kering, peel off gently. Gunakan 1-2x seminggu."
    },
    {
        "id": "53",
        "name": "Bifesta Cleansing Lotion Bright Up",
        "price": 105000,
        "category": "Pembersih",
        "for_conditions": ["Semua Jenis Kulit", "Kulit Kusam"],
        "description": "Cleansing lotion dengan Coenzyme Q10 untuk brightening. All-in-one makeup remover dan facial wash. Water-based formula yang rinse-free. Large 300ml bottle economical.",
        "ingredients": "Coenzyme Q10, Hyaluronic Acid, Vitamin B, Vitamin E",
        "usage": "Tuang ke kapas, wipe seluruh wajah hingga makeup terangkat. Tidak perlu dibilas atau bisa bilas jika prefer."
    },
    {
        "id": "54",
        "name": "Ishizawa Lab Keana Nadeshiko Rice Mask",
        "price": 125000,
        "category": "Masker",
        "for_conditions": ["Pori Besar", "Kulit Berminyak", "Kulit Kusam"],
        "description": "Wash-off mask dengan 100% Rice ingredients untuk pore care. Rice Ceramide dan Rice Bran untuk tighten pores dan brighten. Traditional Japanese beauty secret. Can be used daily.",
        "ingredients": "Rice Ceramide, Rice Bran, Rice Extract, Rice Ferment",
        "usage": "Aplikasikan ke wajah bersih, hindari mata dan bibir. Biarkan 5-10 menit, bilas. Daily use OK."
    },
    {
        "id": "55",
        "name": "Kose Clear Turn Premium Fresh Mask",
        "price": 165000,
        "category": "Masker",
        "for_conditions": ["Kulit Kering", "Anti Aging", "Kulit Kusam"],
        "description": "Premium sheet mask dengan Royal Jelly dan 5 types Collagen. Super thick sheet dengan 55ml essence. Intensive hydration dan anti-aging. Box berisi 4 sheets untuk weekly treatment.",
        "ingredients": "Royal Jelly, 5 Types Collagen, Hyaluronic Acid, Placenta, Vitamin C",
        "usage": "Aplikasikan ke wajah bersih, biarkan 10-20 menit, remove, pat remaining essence. 1-2x seminggu."
    },
    {
        "id": "56",
        "name": "PDC Wafood Made Sake Lees Mask",
        "price": 135000,
        "category": "Masker",
        "for_conditions": ["Kulit Kusam", "Pori Besar", "Kulit Berminyak"],
        "description": "Wash-off mask dengan Sake Lees untuk brightening dan pore refining. Traditional Japanese ingredient untuk translucent skin. Absorbs excess sebum dan removes impurities. Creamy texture.",
        "ingredients": "Sake Lees, Rice Bran, Job's Tears Extract, Collagen",
        "usage": "Aplikasikan layer tebal ke wajah, tunggu 5 menit, massage dengan air, bilas. 2-3x seminggu."
    },
    {
        "id": "57",
        "name": "Meishoku Bigansui Skin Lotion",
        "price": 85000,
        "category": "Toner",
        "for_conditions": ["Jerawat", "Kulit Berminyak", "Pori Besar"],
        "description": "Medicated lotion untuk acne dan oily skin. Salicylic Acid dan Homosulfamine untuk anti-acne. Controls excess sebum dan tightens pores. Affordable Japanese classic sejak 1885.",
        "ingredients": "Salicylic Acid, Homosulfamine, Glycyrrhetinic Acid, Menthol",
        "usage": "Setelah cleansing, saturate kapas, wipe ke seluruh wajah. Fokus ke area berjerawat. Gunakan AM dan PM."
    },
    {
        "id": "58",
        "name": "Kracie Hadabisei 3D Facial Mask",
        "price": 155000,
        "category": "Masker",
        "for_conditions": ["Kulit Kering", "Anti Aging", "Loss of Elasticity"],
        "description": "3D structure sheet mask dengan superior fit. Royal Jelly, Hyaluronic Acid, dan Collagen untuk anti-aging. Extra thick sheet holds 30ml essence. Box berisi 4 masks untuk intensive care.",
        "ingredients": "Royal Jelly, Hyaluronic Acid, Collagen, Vitamin E, Vitamin C Derivative",
        "usage": "Unfold mask, align dengan wajah, biarkan 15 menit, remove, massage remaining essence. 1-2x seminggu."
    },
    {
        "id": "59",
        "name": "Lululun Precious White Sheet Mask",
        "price": 275000,
        "category": "Masker",
        "for_conditions": ["Hiperpigmentasi", "Kulit Kusam", "Anti Aging"],
        "description": "Premium daily sheet mask dengan L-Ascorbic Acid 2-Glucoside untuk whitening. Pearl Extract dan Rice Ceramide. Ultra soft sheet untuk daily use. 32 sheets per box untuk 1 month treatment.",
        "ingredients": "Vitamin C Derivative, Pearl Extract, Rice Ceramide, Squalane",
        "usage": "Gunakan setiap malam setelah toner, biarkan 10 menit, remove, lanjutkan dengan skincare. Daily use recommended."
    },
    {
        "id": "60",
        "name": "Shiseido Uno Whip Wash Scrub",
        "price": 55000,
        "category": "Pembersih",
        "for_conditions": ["Kulit Kusam", "Pori Besar", "Komedo"],
        "description": "Scrub foam wash dengan micro scrub particles untuk gentle exfoliation. Menghilangkan dead skin cells dan blackheads. Fresh citrus scent. Suitable untuk men dan women.",
        "ingredients": "Scrub Particles, Hyaluronic Acid, Glycerin, Menthol",
        "usage": "Basahi wajah, keluarkan foam, massage dengan circular motion, bilas. Gunakan 2-3x seminggu."
    }
]