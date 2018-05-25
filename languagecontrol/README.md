# LanguageControl

## About LanguageControl

Django's otherwise excellent translation mechanism incorrectly assumes that browsers are always configured to request the user's native language. In many countries however, the overwhelming majority of people use software in English instead of their native language for various reasons, and they typically neither know how to, nor care to, configure their browsers specifically to request a specific language from websites. Users will trust that websites intended to be in their native language will simply be in their native language.

To put it simply: Browsers cannot, and thus do not, accurately reflect the users' native language in all countries.

Django's assumption to the contrary means that in such countries, where people tend to use English-language software for one reason or another, even when a Django project has LANGUAGE_CODE set to a target audience's language, most people who speak that language will see the website in English.

LanguageControl enables developers using Django to set whatever default language they see fit.

### License

This app is distributed under the MIT license. See file `LICENSE` for details. In short, don't worry about it.

## Installation

This installation guide assumes familiarity with how Django apps work, how to configure Django project settings and that `LocaleMiddleware` is being used for translating strings from English into some other language.

Start by copying the app in its entirety into your project, right alongside your other apps.

Add `languagecontrol.middleware.LanguageControlMiddleware` to your `MIDDLEWARE_CLASSES` setting, before `LocaleMiddleware` but after `SessionMiddleware`.

Then add `languagecontrol` to the `INSTALLED_APPS` setting.

Your project will then ignore the browser's requests and set the default language to whatever's set in your `LANGUAGE_CODE` setting.

## User-selected language

For projects in which users must be able to select a different language from the default, a function, `set_language(request, language)` is provided in `languagecontrol.utils`, which will set the language for the running session, reverting back to the default language on logout. It can be used when a user selects a preferred language as well, to update the language used in the running session.

To set the user's preferred language at login, however, you'll have to set up a signal receiver in your project to fetch the preferred language from wherever it is stored. It's quite simple, as shown here assuming that the user's preferred language is stored in `user.userprofile.language`:

    from django.contrib.auth.signals import user_logged_in
    from django.dispatch import receiver

    @receiver(user_logged_in)
    def set_language_on_login(sender, user, request, **kwargs):
        set_language(request, user.userprofile.language)
