{% load i18n %}

{% blocktrans %}You are receiving this email because you (or someone pretending to be you) requested that your password be reset on the {{ domain }} site. If you do not wish to reset your password, please ignore this message.{% endblocktrans %}

{% blocktrans %}To reset your password, please click the following link, or copy and paste it into your web browser:{% endblocktrans %}

[{% trans 'Reset password' %}]({{ protocol }}://{{ domain }}{% url 'auth_password_reset_confirm' uid token %})

{% blocktrans %}Your username, in case you've forgotten:{% endblocktrans %} `{{ user.username }}`

