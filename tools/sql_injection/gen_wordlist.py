import itertools

def generate_surakarta_wordlist():
    # Komponen utama yang berkaitan dengan Surakarta & Pemkot
    bases = [
        "surakarta", "pemkot", "solo", "spiritofjava", "kominfo", "diskominfosurakarta",
        "admin", "root", "pemerintah", "walikota", "setda", "bengawan", "batik",
        "keraton", "balaikota", "jateng", "surakartaid", "smartcity", "ska", "sloska",
        "sukowati", "mangkunegaran", "kasunanan", "manahan", "purwosari", "jebres", "laweyan",
        "slametriyadi", "gladag", "ngarsopuro", "pasargedhe", "klewer", "vastenburg", 
        "pandawa", "pajang", "kartasura", "colomadu", "grogol", "palur"
    ]
    
    # Variasi angka & tahun
    numbers = [str(i) for i in range(1001)] + ["2010", "2015", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "12345", "54321", "000000"]
    
    # Simbol umum
    symbols = ["!", "@", "#", "$", "_", ".", "*"]
    
    # Suffixes umum di Indonesia
    suffixes = ["oke", "sip", "jaya", "mantap", "bisa", "juara", "sukses"]

    wordlist = set()

    # 1. Base variations (Case sensitive)
    for b in bases:
        wordlist.add(b)
        wordlist.add(b.upper())
        wordlist.add(b.capitalize())
        
    # 2. Base + Number (0-1000)
    for b in ["admin", "root", "surakarta", "solo", "pemkot"]:
        for n in numbers:
            wordlist.add(f"{b}{n}")
            wordlist.add(f"{b.capitalize()}{n}")
            wordlist.add(f"{n}{b}")

    # 3. Base + Suffix
    for b in bases:
        for s in suffixes:
            wordlist.add(f"{b}{s}")
            wordlist.add(f"{b}_{s}")
            wordlist.add(f"{b.capitalize()}{s}")

    # 4. Double Base + Numbers 샘플 (Limited to 50k to avoid huge file)
    count = 0
    for b1, b2 in itertools.permutations(bases, 2):
        if count > 50000: break
        wordlist.add(f"{b1}{b2}")
        wordlist.add(f"{b1}_{b2}")
        wordlist.add(f"{b1}{b2}123")
        count += 3

    # 5. Massive Symbol Injection
    current_list = list(wordlist)
    for w in current_list:
        if len(wordlist) > 150000: break
        wordlist.add(f"{w}!")
        wordlist.add(f"{w}@")
        wordlist.add(f"@{w}")

    # Simpan ke file
    with open("targeted_wordlist.txt", "w") as f:
        for word in sorted(wordlist):
            f.write(f"{word}\n")
    
    print(f"[+] Berhasil membuat {len(wordlist)} kombinasi kata sandi di 'targeted_wordlist.txt'")

if __name__ == "__main__":
    generate_surakarta_wordlist()
