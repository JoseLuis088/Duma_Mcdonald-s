import os
import time
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

class DumaAssistant:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.assistant_id = os.getenv("ASSISTANT_ID")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    def run_analysis(self, context_data: str):
        """
        Creates a thread, sends the context, and polls for the response.
        """
        try:
            # 1. Create Thread
            thread = self.client.beta.threads.create()
            
            # 2. Add Message
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"Análisis solicitado para los siguientes datos:\n\n{context_data}"
            )
            
            # 3. Create Run
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id,
                additional_instructions="""REGLA CRÍTICA: Debes analizar el equipo específico proporcionado en el resumen (Máquina de Nieve o Máquina de Sodas). 
Si el resumen incluye datos de Presión (Sodas), la meta es mantenerse ARRIBA de 20 PSI. Valores menores indican fallas críticas.
No menciones marcas específicas como Taylor. Tu reporte debe ser ejecutivo, proactivo y centrado en la rentabilidad y mantenimiento preventivo."""
            )
            
            # 4. Polling loop
            start_time = time.time()
            while True:
                # Timeout after 60 seconds
                if time.time() - start_time > 60:
                    return "Error: Timeout en el análisis de IA."
                
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'cancelled', 'expired']:
                    return f"Error en el asistente: {run_status.status}"
                
                time.sleep(1.5)
            
            # 5. Fetch Messages
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            # The assistant's response is the latest message
            for msg in messages:
                if msg.role == 'assistant':
                    # Support for multiple content pieces or just text
                    return msg.content[0].text.value
            
            return "No se recibió respuesta del asistente."

        except Exception as e:
            return f"Excepción en el agente IA: {str(e)}"

# Singleton-like instance
duma_agent = DumaAssistant()
