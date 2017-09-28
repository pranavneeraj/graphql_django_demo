import graphene
from django.contrib.auth import get_user_model
from graphene import relay, AbstractType, Node, InputObjectType, InputField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from courses.models import Developer, Project

class UserNode(DjangoObjectType):
    class Meta:
        model = get_user_model()
        interfaces = (Node,)

class DeveloperNode(DjangoObjectType):
    class Meta:
        model = Developer
        filter_fields = ['user', 'user__username', 'user__first_name']
        interfaces = (Node,)


class ProjectNode(DjangoObjectType):
    developers = graphene.List(DeveloperNode)
    @graphene.resolve_only_args
    def resolve_developers(self):
        return self.developers.all()
    class Meta:
        model = Project
        filter_fields = {
            'name' : ['exact', 'icontains', 'istartswith'],
            'summary' : ['icontains', 'istartswith'],
            'developers':['exact'],
            'developers__user__first_name':['exact'],
        }

        interfaces = (Node,)


class CreateDeveloper(graphene.Mutation):
    class Input:
        user = graphene.String(required=True)

    developer = graphene.Field(DeveloperNode)

    @classmethod
    def mutate(self, cls, input, context, info):
        user=input.get("user")
        developer = Developer(user_id=user)
        developer.save()
        return CreateDeveloper(developer=developer)


class CreateProject(graphene.ClientIDMutation):
    class Input:
        name = graphene.String()
        summary = graphene.String()
        developers = graphene.List(graphene.Int)

    project = graphene.Field(ProjectNode)

    @classmethod
    def mutate_and_get_payload(cls, input, context, info):
        name = input.get('name')
        summary = input.get('summary')
        developers = input.get("developers")
        try:
            developers = list(developers)
        except ValueError:
            try:
                for developer_id in developers:
                    _type, developers= Node.from_global_id(input.get("developer_id"))
                    assert _type == 'DeveloperNode', 'Found {} instead of developer'.format(_type)
                developers = list(developers)
            except:
                raise Exception("Received Invalid Developer id: {}".format(developer_id))
        project = Project(name=name, summary=summary)
        project.save()
        for developer_id in developers:
            developer = Developer._meta.model.objects.get(id=developer_id)
            project.developers.add(developer)
        project.developers = project.developers.all()
        return CreateProject(project=project)


class UpdateDeveloper(graphene.Mutation):
    class Input:
        user_id = graphene.String(required=True)
        id = graphene.String()

    developer = graphene.Field(DeveloperNode)

    @classmethod
    def mutate(self, cls, input, context, info):
        id = input.get("id")
        try:
            id = int(id)
        except ValueError:
            try:
                _type, id = Node.from_global_id(input.get("id"))
                assert _type == 'DeveloperNode', 'Found {} instead of developer'.format(_type)
                id = int(id)
            except:
                raise Exception("Received Invalid Developer id: {}".format(id))
        developer = Developer._meta.model.objects.get(id=id)
        user_id = input.get("user_id")
        
        if user_id is not None:
            developer.user_id = user_id
        developer.save()
        return UpdateDeveloper(developer=developer)

class DeleteProject(graphene.Mutation):
    class Input:
        name = graphene.String()
        id = graphene.String()

    project = graphene.Field(ProjectNode)


    @classmethod
    def mutate(self, cls, input, context, info):
        id = input.get("id")
        try:
            id = int(id)
        except ValueError:
            try:
                _type, id = Node.from_global_id(input.get("id"))
                assert _type == 'ProjectNode', 'Found {} instead of project'.format(_type)
                id = int(id)
            except:
                raise Exception("Received Invalid Project id: {}".format(id))
        project = Project._meta.model.objects.get(id=id)
        if project is not None:
            project.delete()
        return DeleteProject(project=project)



class ProjectMutations(AbstractType):
    create_developer = CreateDeveloper.Field()
    create_project = CreateProject.Field()
    update_developer = UpdateDeveloper.Field()
    delete_project = DeleteProject.Field()


class Query(AbstractType):
    user  = Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)
    developer = Node.Field(DeveloperNode)
    all_developers = DjangoFilterConnectionField(DeveloperNode)

    project = Node.Field(ProjectNode)
    all_projects = DjangoFilterConnectionField(ProjectNode)
