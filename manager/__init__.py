from .models import graph
from .views import app

app.jinja_env.variable_start_string = '##'
app.jinja_env.variable_end_string = '##'
app.jinja_env.block_start_string = '#%'
app.jinja_env.block_end_string = '%#'
app.jinja_env.comment_start_string = '<#'
app.jinja_env.comment_end_string = '#>'

# schema = graph.schema

# schema.create_uniqueness_constraint('User', 'username')
# schema.create_uniqueness_constraint('User', 'email')
# schema.create_uniqueness_constraint('Project', 'id')
# schema.create_uniqueness_constraint('Job', 'id')
