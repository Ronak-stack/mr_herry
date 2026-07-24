import importlib

def route_handler(state, client, engine, background_tasks):
    intent = state.intent  # e.g., "SQL", "CHAT", "REMINDER"
    
    # 1. Convert intent to matching filename and class name conventions
    # "SQL" -> "sql_handler"
    module_name = f"handlers.{intent.lower()}_handler"
    
    # "SQL" -> "SqlHandler" (or keep as upper if named SQLHandler)
    class_name = f"{intent.capitalize()}Handler"  

    try:
        # 2. Dynamically import the module (e.g., handlers.sql_handler)
        module = importlib.import_module(module_name)
        
        # 3. Get the class from the imported module
        handler_class = getattr(module, class_name)
        
        # 4. Instantiate the handler object with your required arguments
        handler_instance = handler_class(
            state=state, 
            client=client, 
            engine=engine, 
            background_tasks=background_tasks
        )
        
        return handler_instance

    except ModuleNotFoundError:
        return {"error": f"No handler file found for intent: '{intent}'"}
    except AttributeError:
        return {"error": f"Class '{class_name}' not found inside '{module_name}.py'"}
    except Exception as e:
        return {"error": f"Failed to instantiate handler: {str(e)}"}