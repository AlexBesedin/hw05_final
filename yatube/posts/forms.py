from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea,
        label="Введите текст",
        required=True,
        help_text="Текст поста",
    )

    class Meta:
        model = Post
        fields = ("text", "group")
        labels = {"group": "Выберите нужную группу"}
        help_text = {"group": "Группа поста"}
        fields = ("group", "text", "image")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
