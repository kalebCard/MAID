**Flujo de Interacción del Agente de IA**  
*(Versión Normalizada y Estructurada)*  

---

### **1. Procesamiento Inicial del Prompt**  
▸ **Prompt del Usuario**: Recepción de la entrada.  
▸ **Normalización**: Estandarizar formato (ej: eliminar caracteres especiales, corregir mayúsculas).  
▸ **Extraer Información Sensible**:  
   - Identificar datos sensibles (ej: contraseñas, tokens).  
   - **Variables Locales + Encriptación**: Almacenar temporalmente en entorno seguro (ej: AES-256).  

---

### **2. Análisis y Decisión**  
▸ **Análisis de Intención**: Clasificar la tarea (ej: "buscar info", "ejecutar código", "crear subagente").  
▸ **Estandarización**: Convertir la solicitud a un formato estructurado (ej: JSON con campos `acción`, `parámetros`).  
▸ **Búsqueda en Memoria**:  
   - Consultar memoria a corto/largo plazo para contexto histórico o soluciones previas.  

---

### **3. Ejecución de la Tarea**  
**Memoria Corto Plazo**: Crear contexto temporal para la sesión actual.  
**Planificación**: Seleccionar herramientas según la intención:  

| **Herramientas Disponibles**          | **Acciones Específicas**                                      |  
|---------------------------------------|---------------------------------------------------------------|  
| 🔍 **Buscar en la Web**               | - Usar APIs (ej: Google Search, NewsAPI).                     |  
| 🖥️ **Ejecutar Código**               | - **Desencriptar** datos necesarios.                          |  
|                                       | - Detectar lenguaje (Python/JS/Shell) y entorno (local/cloud).|  
| 🛠️ **Modificar Comportamiento**       | - Ajustar parámetros del agente (ej: tono, prioridades).      |  
| 🤖 **Crear Subordinado**              | - Iniciar subagente con tarea/especificaciones definidas.     |  

---

### **4. Validación y Retroalimentación**  
▸ **¿Tarea Cumplida?**  
   - **Sí**: Retornar resultado al usuario (ej: respuesta, archivo, confirmación).  
   - **No**: Reiniciar ciclo con nuevos parámetros (`repetir = true`).  

---

### **5. Aprendizaje y Memoria**  
▸ **Resumen de lo Aprendido**: Extraer patrones o datos útiles (ej: nuevo comando, optimización).  
▸ **Actualizar Memorias**:  
   - **Corto Plazo**: Guardar contexto inmediato para iteraciones actuales.  
   - **Largo Plazo**: Almacenar conocimiento permanente (ej: en base de datos vectorial).  

---

**Diagrama de Flujo Simplificado**:  
```  
Usuario → Normalizar → [Sensitive Data?] → Encriptar → Analizar → Buscar Memoria → Planificar → Herramientas → [Éxito?] → Sí/No → Resumir → Actualizar Memoria → Fin  
```