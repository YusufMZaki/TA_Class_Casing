This is my undergraduate thesis project

# Main

1. Prepare and activate the environment
1. Then run in terminal:

    ``` 
    streamlit run Class_streamlit.py 
    ```

# Environment

1. **Setup environment** <br />

   ```
   conda create --prefix ./.venv python=3.12.4
   ```
   ```
   conda activate ./.venv
   ```

1. **Install requirements** <br />

   ```
   pip install --no-cache-dir -r ./simpleRequirements.txt
   ```
   or
   ```
   pip install --no-cache-dir -r ./fullRequirements.txt
   ```
   
1. **Deactivate enviroment** <br />

   ```
   conda deactivate
   ```

# Might Be Useful

- Remove Environment

   ```
   conda remove --prefix ./.venv --all
   ```

- Freeze The Requirements

   ```
   pip freeze > fullRequirements.txt
   ```

# just in case
https://stackoverflow.com/questions/13716658/how-to-delete-all-commit-history-in-github