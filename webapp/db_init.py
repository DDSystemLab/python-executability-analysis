import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
import django

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Delete all if necessary
# User.objects.all().delete()

try:
    User.objects.create_superuser('admin', 'nima_mahmoudi@live.com', 'pass')
except Exception:
    print("Admin already exists!")

from python_snippets import models
import pandas as pd

# Delete all if necessary
models.PythonSnippet.objects.all().delete()

print('Loading the data from file...')

# data_file_name = '../data/mytable.csv'
data_file_name = '../data/SnippetsAnswerPythonOnly.csv'

df = pd.read_csv(data_file_name, error_bad_lines=False, warn_bad_lines=False)
df = df.where((pd.notnull(df)), None)

print('Loading models onto the db...')

# max_num_rows = min(1000, df.shape[0])
max_num_rows = df.shape[0]

print('num of rows:', max_num_rows)

all_ps = []
for i in range(max_num_rows):
    row = df.iloc[i, :]

    # if row['Id'] == 210207849:
    #     ps = models.PythonSnippet()
    #     ps.original_id = row['Id']
    #     ps.post_id = row['PostId']
    #     ps.pred_post_block_version_id = row['PredPostBlockVersionId']
    #     ps.root_post_block_version_id = row['RootPostBlockVersionId']
    #     ps.length = row['Length']
    #     ps.line_count = row['LineCount']
    #     ps.tags = row['Tags']
    #     ps.content = row['Content']
    #     ps.save()

    ps = models.PythonSnippet()
    ps.original_id = row['Id']
    ps.post_id = row['PostId']
    ps.pred_post_block_version_id = row['PredPostBlockVersionId']
    ps.root_post_block_version_id = row['RootPostBlockVersionId']
    ps.length = row['Length']
    ps.line_count = row['LineCount']
    ps.tags = row['Tags']
    ps.content = row['Content']
    all_ps.append(ps)
    
    # try:
    # ps.save()
    # except Exception:
    #     pass

print('Bulk Saving...')

models.PythonSnippet.objects.bulk_create(all_ps, batch_size=999)
