from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text')
        help_texts = {
            'text': '*введите текст поста',
            'group': 'выберите группу, к которой будет относиться пост'
        }
