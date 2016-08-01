from .models import graph

schema = graph.schema

# schema.create_uniqueness_constraint('User', 'username')
# schema.create_uniqueness_constraint('User', 'email')
# schema.create_uniqueness_constraint('Project', 'id')
# schema.create_uniqueness_constraint('Job', 'id')
