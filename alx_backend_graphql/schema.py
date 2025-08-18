# import graphene
# from crm.schema import Query as CRMQuery

# class Query(CRMQuery, graphene.ObjectType):
#     pass

# schema = graphene.Schema(query=Query)

import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(CRMQuery, graphene.ObjectType):
    pass

class Mutation(CRMMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)  # Must include mutation