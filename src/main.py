import hvplot.pandas
import numpy as np
import panel as pn
import os
import pandas as pd
from ui import TranslationDashboard, ImageTextEditor
from PIL import Image

# Usage example
dashboard = TranslationDashboard(collapsed_sidebar=True)

# Adding editors
images_path = '/workspaces/llmv_translation/images'

for file in os.listdir(images_path):
    if file.endswith(".jpg") or file.endswith(".png"):
        dashboard.append_editor(ImageTextEditor(
            image_object=Image.open(os.path.join(images_path, file))))
# dashboard.append_editor(ImageTextEditor(
#     image_object=Image.open("/workspaces/llmv_translation/images/1-14_rotated_page-0003.jpg")))
# dashboard.append_editor(ImageTextEditor(
#     image="/workspaces/llmv_translation/images/1-14_rotated_page-0004.jpg"))
# dashboard.append_editor(ImageTextEditor(
#     image="/workspaces/llmv_translation/images/1-14_rotated_page-0005.jpg"))
# dashboard.append_editor(ImageTextEditor(
#     image="/workspaces/llmv_translation/images/1-14_rotated_page-0006.jpg"))


dashboard.servable()