import pathlib

# In[37]:


project = pathlib.Path().cwd()
app = project / "app"
data = project / "data"
pw = data / "passwords"
user = data / "usernames"
database_dir = project / "database"
database_dir.mkdir(exist_ok=True)
db = database_dir / "creads.db"
