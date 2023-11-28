import hvplot.pandas
import numpy as np
import panel as pn
import pandas as pd
from ui import TranslationDashboard, ImageTextEditor

# Usage example
dashboard = TranslationDashboard(collapsed_sidebar=True)

# Adding editors
dashboard.append_editor(ImageTextEditor(
    image="/workspaces/llmv_translation/images/1-14_rotated_page-0003.jpg"))
dashboard.append_editor(ImageTextEditor(
    image="/workspaces/llmv_translation/images/1-14_rotated_page-0004.jpg"))
dashboard.append_editor(ImageTextEditor(
    image="/workspaces/llmv_translation/images/1-14_rotated_page-0005.jpg"))
dashboard.append_editor(ImageTextEditor(
    image="/workspaces/llmv_translation/images/1-14_rotated_page-0006.jpg"))


dashboard.servable()