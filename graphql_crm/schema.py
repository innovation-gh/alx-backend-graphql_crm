import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(CRMQuery, graphene.ObjectType):
    # This combines all query definitions from crm/schema.py
    pass

class Mutation(CRMMutation, graphene.ObjectType):
    # This combines all mutation definitions from crm/schema.py
    pass

# This schema configuration enables both queries and mutations
schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    auto_camelcase=False  # Optional: preserves exact field names
)