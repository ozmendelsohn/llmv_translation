import base64
import panel as pn
import param
from PIL import Image
import io

from translate import OpenAITranslator
from prompt import create_prompt

pn.extension('texteditor')


def create_text_editor():
    toolbar = [
        ['bold', 'italic', 'underline', 'strike'],        # toggled buttons
        ['blockquote', 'code-block'],

        [{'list': 'ordered'}, {'list': 'bullet'}],
        [{'indent': '-1'}, {'indent': '+1'}],          # outdent/indent
        [{'direction': 'rtl'}],                         # text direction

        [{'header': [1, 2, 3, 4, 5, 6, False]}],

        [{'color': []}, {'background': []}],          # dropdown with defaults from theme
        [{'font': []}],
        [{'align': []}],

        ['clean']                                         # remove formatting button
    ]
    return pn.widgets.TextAreaInput(name='Translated Text',
                                    height=1000,
                                    width_policy='max',
                                    sizing_mode='stretch_width',)
    return pn.widgets.TextEditor(name='Translated Text',
                                 height=1000,
                                 width_policy='max',
                                 sizing_mode='stretch_width',
                                 toolbar=toolbar)


class ImageTextEditor(param.Parameterized):
    image_object = param.Parameter()
    base64_image = param.String(default="")
    text = param.String(default="Translated text will appear here.")

    def __init__(self, **params):
        super(ImageTextEditor, self).__init__(**params)
        self.text_editor = create_text_editor()
        self.text_editor.value = self.text  # Initialize the text editor with the default text
        self.convert_image_to_base64()  # Convert the image object to base64

    def convert_image_to_base64(self):
        if self.image_object:
            buffered = io.BytesIO()
            self.image_object.save(buffered, format="JPEG")  # Adjust format if needed
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            self.base64_image = img_str

    def get_base64_image(self):
        return self.base64_image

    @param.depends('text', watch=True)
    def update_text_editor(self):
        self.text_editor.value = self.text  # This method will be called when 'text' changes

    def set_text(self, new_text):
        self.text = new_text
        self.text_editor.value = new_text  # Ensure the widget updates

    def view(self):
        min_image_height = 1000  # Minimum height for the image
        image_pane = pn.pane.Image(self.image_object,
                                   height=min_image_height,
                                   sizing_mode='fixed',
                                   align='center')
        return pn.Row(image_pane, self.text_editor)


class TranslationDashboard(pn.template.MaterialTemplate):
    def __init__(self, **params):
        super(TranslationDashboard, self).__init__(**params)
        self.title = 'Translation Dashboard'
        self.api_key_input = pn.widgets.PasswordInput(name='API Key', placeholder='Enter OpenAI API key...')
        self.file_input = pn.widgets.FileInput(name='Upload Images', accept='.png,.jpg,.jpeg', multiple=True)
        self.from_language_input = pn.widgets.Select(name='From Language', options=['English', 'Hebrew', 'Spanish', 'French'])
        self.to_language_input = pn.widgets.Select(name='To Language', options=['Hebrew', 'English', 'Spanish', 'French'])
        self.file_input.param.watch(self.on_file_input, 'value')
        self.generate_all_button = pn.widgets.Button(name='Generate All', button_type='primary')
        self.export_file_name_input = pn.widgets.TextInput(name='Export File Name', value='Translation.txt')
        self.export_text_button = pn.widgets.Button(name='Export Text', button_type='primary')
        self.sidebar.append(self.api_key_input)
        self.sidebar.append(self.file_input)
        self.sidebar.append(self.generate_all_button)
        self.sidebar.append(self.from_language_input)
        self.sidebar.append(self.to_language_input)
        self.sidebar.append(pn.Row(self.export_file_name_input, self.export_text_button))
        self.image_text_editors = []
        self.main.append(self.create_dashboard())
        self.generate_all_button.on_click(self.generate_translation_all)

    def on_file_input(self, event):
        for file in self.file_input.value:
            image_stream = io.BytesIO(file)
            image = Image.open(image_stream)
            editor = ImageTextEditor(image_object=image)
            self.append_editor(editor)

    def create_dashboard(self):
        self.panel_objects = []  # overwrite the existing panel_objects
        dashboard = pn.Column(sizing_mode='stretch_width', scroll=True)
        for editor in self.image_text_editors:
            generate_button = pn.widgets.Button(name='Generate', button_type='primary')
            generate_button.on_click(self.generate_translation)

            editor_view = editor.view()
            self.panel_objects.append((generate_button, editor_view))
            dashboard.append(pn.Column(generate_button, editor_view, sizing_mode='stretch_width'))
        return dashboard

    def append_editor(self, editor):
        self.image_text_editors.append(editor)
        # Rebuild the dashboard with the new editor
        self.main.clear()  # Clear the existing layout
        self.main.append(self.create_dashboard())  #

    def generate_translation(self, event):
        # Find the index of the button that was clicked
        button_index = next((i for i, obj in enumerate(self.panel_objects) if obj[0] is event.obj), None)
        self.generate_translation_single_text_editor(button_index)
    
    def generate_translation_single_text_editor(self, button_index):
        if button_index is not None:
            # Get the corresponding ImageTextEditor object
            editor = self.image_text_editors[button_index]

            # Create an OpenAITranslator object using the API key from the sidebar
            api_key = self.api_key_input.value
            translator = OpenAITranslator(api_key)

            # Create a prompt (placeholder for now)
            previous_page = button_index - 1 if button_index > 0 else None
            previous_page_text = self.image_text_editors[previous_page].text if previous_page is not None else None
            previous_page_text = None if previous_page_text == "Translated text will appear here." else previous_page_text
            prompt = create_prompt(previous_page_text,
                                   from_language=self.from_language_input.value,
                                   to_language=self.to_language_input.value)

            # Get the base64 image from the ImageTextEditor object
            base64_image = editor.get_base64_image()

            # Call the translate_image function of the translator
            self.modal.append("Translating... Editor index: " + str(button_index))
            self.open_modal()
            translated_text = translator.translate_image(base64_image, prompt, max_tokens=4000)
            self.close_modal()

            # Set the translated text in the ImageTextEditor's text editor
            editor.set_text(translated_text)  # This will update the text_editor's value
            
    def generate_translation_all(self, event):
        for i in range(len(self.image_text_editors)):
            self.generate_translation_single_text_editor(i)
    
    def export_text(self, event):
        # Open a file for writing
        with open(self.export_file_name_input.value, 'w') as file:
            # Iterate over the image text editors
            for editor in self.image_text_editors:
                # Get the text from each editor
                text = editor.text
                # check if the text is the default text
                if text == "Translated text will appear here.":
                    text = ""
                # Write the text to the file
                file.write(text + "\n")
        
            

if __name__ == '__main__':
    import os
    # Usage example
    dashboard = TranslationDashboard(collapsed_sidebar=True)

    # Adding editors
    images_path = '/workspaces/llmv_translation/images'

    for file in os.listdir(images_path):
        if file.endswith(".jpg") or file.endswith(".png"):
            dashboard.append_editor(ImageTextEditor(
                image_object=Image.open(os.path.join(images_path, file))))
            
    # dashboard.main.objects[0][1].objects[0].show()
    dashboard.show()
    ben = 4
            

