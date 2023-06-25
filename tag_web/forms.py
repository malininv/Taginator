from django.forms import ModelForm, TextInput, Textarea
from .models import Tag, Post, MAX_TAG_LENGTH


class FormCreateTag(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].initial = ''

    template_name = 'tag_web/form-create-tag.html'

    class Meta:
        model = Tag
        fields = ['name']
        error_messages = {
            "name": {
                "max_length": f"Максимальная длина тега {MAX_TAG_LENGTH} символов.",
            },
        }

        widgets = {
            'name': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Название тега...',
                })
        }


class FormCreatePost(ModelForm):
    def __init__(self, *args, **kwargs):
        tg_id = kwargs.pop('tg_id')
        super().__init__(*args, **kwargs)
        if tg_id:
            self.fields['tag'].queryset = Tag.objects.filter(telegram_user__tg_id=tg_id)
            self.fields['tag'].widget.attrs['class'] = 'form-select'

    template_name = 'tag_web/form-create-post.html'

    class Meta:
        model = Post
        fields = ['tag', 'text']

        widgets = {
            'text': Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Пост...',
                })
        }

# class EditTagForm(ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['name'].initial = ''
#
#     template_name = 'tag_web/form-create-tag.html'
#
#     tag =
#     class Meta:
#         model = Tag
#         fields = ['name']
#         error_messages = {
#             "name": {
#                 "max_length": f"Максимальная длина тега {MAX_TAG_LENGTH} символов.",
#             },
#         }
#
#         widgets = {
#             'name': TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Введите название тега',
#             })
#         }
