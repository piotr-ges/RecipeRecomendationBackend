import csv
import ast
from api.models import Recipe

def import_recipes_from_csv(csv_file_path):
    success = 0
    failed = 0

    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                ingredients = ast.literal_eval(row['ingredients'])
                directions = ast.literal_eval(row['directions'])
                ner = ast.literal_eval(row['NER'])

                Recipe.objects.create(
                    title=row['title'][:255],  # ogranicz długość, jeśli pole jest krótsze
                    ingredients=ingredients,
                    directions=directions,
                    link=row['link'],
                    source=row['source'],
                    ner=ner,
                    site=row['site']
                )
                success += 1
            except Exception as e:
                print(f"⚠️ Błąd w wierszu: {row.get('title', '[brak tytułu]')}")
                print(f"   Powód: {e}")
                failed += 1

    print(f"\n✅ Zakończono import: {success} dodanych, {failed} pominiętych.")