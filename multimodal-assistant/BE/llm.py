from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration, BlipForQuestionAnswering
from PIL import Image
import fitz  # PyMuPDF for PDF parsing
import docx

# --- General QA ---
general_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

# --- Document QA ---
doc_qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# --- BLIP models for vision ---
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
blip_qa_model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")
blip_cap_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Contexts
doc_context = None
image_path = None


def set_doc_context(text: str):
    global doc_context
    doc_context = text


def set_image_context(path: str):
    global image_path
    image_path = path


def describe_image(path: str) -> str:
    try:
        raw_image = Image.open(path).convert("RGB")
        inputs = blip_processor(raw_image, return_tensors="pt")
        out = blip_cap_model.generate(**inputs, max_new_tokens=50)
        return blip_processor.decode(out[0], skip_special_tokens=True)
    except Exception as e:
        print("describe_image error:", e)
        return "Could not generate image description."


def answer_question(question: str, context: str = None) -> str:
    global doc_context, image_path
    try:
        if context == "doc" and doc_context:
            result = doc_qa_pipeline(question=question, context=doc_context)
            return result.get("answer", "No answer found.")

        elif context == "image" and image_path:
            raw_image = Image.open(image_path).convert("RGB")
            inputs = blip_processor(raw_image, question, return_tensors="pt")
            out = blip_qa_model.generate(**inputs, max_new_tokens=50)
            return blip_processor.decode(out[0], skip_special_tokens=True)

        else:  # Basic General QA
            prompt = f"Answer the question concisely: {question}"
            result = general_pipeline(prompt, max_new_tokens=50)
            return result[0]["generated_text"]

    except Exception as e:
        print("answer_question error:", e)
        return "Error generating answer."


def extract_text_from_pdf(path: str) -> str:
    try:
        text = ""
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text()
        return text
    except:
        return ""


def extract_text_from_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text
    except:
        return ""
