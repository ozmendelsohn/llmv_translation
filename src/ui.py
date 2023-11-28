import base64
import panel as pn
import param

from translate import OpenAITranslator

pn.extension('texteditor')


class ImageTextEditor(param.Parameterized):
    image = param.Parameter()
    text = param.String(default="Translated text will appear here.")

    def __init__(self, **params):
        super(ImageTextEditor, self).__init__(**params)
        self.text_editor = pn.widgets.TextEditor(name='Translated Text', 
                                                 height=1000, 
                                                 width_policy='max',
                                                 sizing_mode='stretch_width')
        self.text_editor.value = self.text  # Initialize the text editor with the default text
    
    @staticmethod
    def encode_image_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def get_base64_image(self):
        return self.encode_image_to_base64(self.image)
        
    @param.depends('text', watch=True)
    def update_text_editor(self):
        self.text_editor.value = self.text  # This method will be called when 'text' changes

    def set_text(self, new_text):
        # Set the new text in both the parameter and the widget
        self.text = new_text
        self.text_editor.value = new_text  # Ensure the widget updates
        
    def view(self):
        min_image_height = 1000  # Minimum height for the image
        image_pane = pn.pane.Image(self.image, 
                                   height=min_image_height, 
                                   sizing_mode='fixed', 
                                   align='center')
        # Return a new row for each call to ensure unique widgets
        return pn.Row(image_pane, self.text_editor)


class TranslationDashboard(pn.template.MaterialTemplate):
    def __init__(self, **params):
        super(TranslationDashboard, self).__init__(**params)
        self.title = 'Translation Dashboard'
        self.api_key_input = pn.widgets.TextInput(name='API Key', placeholder='Enter OpenAI API key...')
        self.sidebar.append(self.api_key_input)
        self.sidebar.append(pn.widgets.Button(name='Generate All', button_type='primary'))
        self.image_text_editors = []

        self.panel_objects = []  # This will hold the tuples of (button, editor view)
        self.main.append(self.create_dashboard())

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
        self.main[0] = self.create_dashboard()

    def generate_translation(self, event):
        # Find the index of the button that was clicked
        button_index = next((i for i, obj in enumerate(self.panel_objects) if obj[0] is event.obj), None)
        if button_index is not None:
            # Get the corresponding ImageTextEditor object
            editor = self.image_text_editors[button_index]

            # Create an OpenAITranslator object using the API key from the sidebar
            api_key = self.api_key_input.value
            translator = OpenAITranslator(api_key)

            # Create a prompt (placeholder for now)
            prompt = """
Please help me to translate the following book from English to Hebrew.
I am going to upload one page each messages then you will only write the translate version.
Please notice that sometimes a sentence will start in on page and will end in the next one, please wait for the full 
sentence in the text page than write it under the current page."""

            # Get the base64 image from the ImageTextEditor object
            base64_image = editor.get_base64_image()

            # Call the translate_image function of the translator
            translated_text = translator.translate_image(base64_image, prompt)

            # Set the translated text in the ImageTextEditor's text editor
            editor.set_text(translated_text)  # This will update the text_editor's value
