import re
class InfoSecure:
    def extract_data(text):
        sensitive_data = re.findall(r"\*\*(.*?)\*\*", text)
        modified_text = re.sub(r"\*\*(.*?)\*\*", lambda m: f"{{ID_{sensitive_data.index(m.group(1))}}}", text)
        return modified_text, sensitive_data

    def restore_data(modified_text, sensitive_data):
        for i, data in enumerate(sensitive_data):
            modified_text = modified_text.replace(f"{{ID_{i}}}", f"**{data}**")
        return modified_text
