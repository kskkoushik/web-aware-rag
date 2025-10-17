from unstructured.partition.html import partition_html
from unstructured.chunking.basic import chunk_elements

def chunk_html_content(html_content:str , chunk_size=3500, chunk_overlap=700):


    elements = partition_html(text=html_content)

    chunks = chunk_elements(
         elements=elements,
         max_characters=chunk_size,
         new_after_n_chars=700,
         overlap=chunk_overlap
    )

    processed_chunks = [chunk.text for chunk in chunks]

    print(processed_chunks)

    return processed_chunks







