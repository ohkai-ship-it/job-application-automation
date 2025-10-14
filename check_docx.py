from docx import Document

doc = Document('output/cover_letters/CoverLetter_Infopro_Digital_20251014_105216.docx')

print("=" * 80)
print("DOCX CONTENT ANALYSIS")
print("=" * 80)

for i, para in enumerate(doc.paragraphs[:25]):
    print(f"{i:2d}: {para.text}")
