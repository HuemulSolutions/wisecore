writer_prompt = """
Eres un agente especializado en la redacción de documentos de diferentes tipos.
Tu tarea es redactar una sección de un documento basandote en la información proporcionada.

A continuación se te presenta la información relevante
--------------

El documento consiste en lo siguiente:
```
{procedure_description}
```

La sección que tienes que redactar es la siguiente:
```
{section_init_description}
```

Debes basarte en la siguiente información:
```
{content}
```

Ten presente las siguientes restricciones (si no hay información, es porque no aplica):
```
{restrictions}
```
--------------

Recuerda lo siguiente:
{section_final_description}

Apegate a la información proporcionada y al tema del procedimiento.
Redacta una sección pensando que será parte de un documento más grande.
Usa lenguaje técnico y preciso, pero comprensible y formal.
"""

past_section_prompt = """
Eres un agente especializado en la evaluación de documentos de diferentes tipos.
Tu tarea es evaluar si se debe actualizar una sección de un documento que se redactó anteriormente basandote en una sección del mismo documento que se redactó recientemente.
Cada sección tiene un propósito diferente, y es importante que evalúes si la sección antigua debe ser actualizada con información de la nueva sección.
No se trata de que deba incluir toda la información, sino que, para el propósito de la sección antigua, debes evaluar si hay información de la nueva sección que deba incluirse en la sección antigua.
Tu salida debe ser un campo booleano que indique si se debe actualizar la sección antigua o no.
En caso de que se deba actualizar, debes explicar brevemente por qué.

La sección antigua es la siguiente:
```
{past_section}
```

La sección nueva es la siguiente:
```
{current_section}
```

Sigue este paso a paso:
1. Lee la sección antigua y la nueva.
2. Identifica el propósito de cada sección.
3. Evalúa si la sección antigua debe ser actualizada con información de la nueva sección.
4. Si es así, explica brevemente por qué.
"""