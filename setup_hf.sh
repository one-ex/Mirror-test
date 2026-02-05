# Setup Repository untuk Hugging Face Spaces

cd /home/exball/Project/Mirror-test

# Inisialisasi Git repository (jika belum)
git init

# Tambahkan semua file Hugging Face
git add app.py requirements.txt README.md .gitignore
git commit -m "Initial commit: PixelDrain Mirror Service for Hugging Face Spaces"

# Buat branch main (HF menggunakan main)
git branch -M main

# Lihat status
echo "✅ Repository siap untuk Hugging Face Spaces!"
echo ""
echo "📁 File yang akan diupload:"
ls -la
echo ""
echo "🔧 Langkah selanjutnya:"
echo "1. Login ke https://huggingface.co/spaces"
echo "2. Klik 'Create New Space'"
echo "3. Pilih 'Docker' sebagai SDK"
echo "4. Upload file-file ini"
echo "5. Set environment variable: PIXELDRAIN_API_KEY"
echo "6. Deploy!"