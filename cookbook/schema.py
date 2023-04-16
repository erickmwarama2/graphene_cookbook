import graphene
from graphene_django import DjangoObjectType
from graphene import relay

from ingredients.models import Category, Ingredient

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "ingredients")

class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "notes", "category")

class CategoryNode(graphene.ObjectType):
    category_name = graphene.String()

    class Meta:
        interfaces = (graphene.Node, )

    def resolve_category_name(instance, info):
        return instance.name

class CategoryConnection(relay.Connection):
    total_count = graphene.Int()

    class Meta:
        node = CategoryNode


    def resolve_total_count(instance, info):
        return Category.objects.count()

class IngredientMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        notes = graphene.String(required=True)
        category = graphene.Int(required=True)

    ingredient = graphene.Field(IngredientType)

    @classmethod
    def mutate(cls, root, info, name, notes, category):
        ingredient = Ingredient(name=name, notes=notes, category_id=category)
        ingredient.save()

        return IngredientMutation(ingredient=ingredient)

class CategoryMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    category = graphene.Field(CategoryType)

    @classmethod
    def mutate(cls, root, info, name):
        category = Category(name=name)
        category.save()

        return CategoryMutation(category=category)

class MyMutation(graphene.ObjectType):
    create_category = CategoryMutation.Field()
    create_ingredient = IngredientMutation.Field()

class Query(graphene.ObjectType):
    all_ingredients = graphene.List(IngredientType)
    category_by_name = graphene.Field(CategoryType, name=graphene.String(required=True))
    categories = relay.ConnectionField(CategoryConnection)

    def resolve_categories(root, info):
        return Category.objects.all()

    def resolve_all_ingredients(root, info):
        return Ingredient.objects.select_related("category").all()

    def resolve_category_by_name(root, info, name):
        try:
            return Category.objects.get(name=name)
        except Category.DoesNotExist:
            return None

schema = graphene.Schema(query=Query, mutation=MyMutation)