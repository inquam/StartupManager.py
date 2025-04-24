  # Example for a Python script
  app_name = "MyPythonApp"
  app_path = sys.argv[0]  # Current script path
  
  # Create a startup manager
  manager = StartupManager(app_name, app_path)
  
  # Check if the app is enabled to run at startup
  print(f"Is enabled: {manager.is_enabled()}")
  
  # Enable the app to run at startup
  if manager.enable():
      print(f"Successfully enabled {app_name} to run at startup")
  else:
      print(f"Failed to enable {app_name} to run at startup")
  
  # Disable the app from running at startup
  if manager.disable():
      print(f"Successfully disabled {app_name} from running at startup")
  else:
      print(f"Failed to disable {app_name} from running at startup")
