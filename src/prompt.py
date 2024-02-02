PROMPT_TEMPLATE = """
Please translate the following book page from {from_language} to {to_language}.
I am going to upload one page each messages then you will only write the translate version.
Please try to recreate the the same paragraphs.
Please notice that sometimes a sentence will start in on page and will end in the next one, please wait for the full 
sentence in the text page than write it under the current page.
ONLY WRITE THE TRANSLATION, DO NOT WRITE ANYTHING ELSE.
"""

def create_prompt(previous_page=None,
                  from_language='English',
                  to_language='Hebrew'):
    promnt_template = PROMPT_TEMPLATE.format(from_language=from_language, to_language=to_language)
    if previous_page is None:
        return promnt_template
    else:
        return promnt_template + f"\nPervious page:\n{previous_page}"