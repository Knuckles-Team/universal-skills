try:
    from pypdf import PdfReader
except ImportError:
    print("Error: Missing required dependencies for the 'document-tools' skill.")
    print(
        "Please install them by running: pip install 'universal-skills[document-tools]'"
    )
    import sys

    sys.exit(1)
import sys

reader = PdfReader(sys.argv[1])
if reader.get_fields():
    print("This PDF has fillable form fields")
else:
    print(
        "This PDF does not have fillable form fields; you will need to visually determine where to enter data"
    )
