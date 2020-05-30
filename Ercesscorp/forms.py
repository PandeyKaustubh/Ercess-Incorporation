from django import forms
import re

from .porter import PURPOSE__CHOICES, GENDER__CHOICES, LOCATION__CHOICES
from dashboard.models import Articles2


class UserForm(forms.Form):

    firstname = forms.CharField(
        # label='username',
        widget=forms.TextInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Firstname *'

            }
        )
    )
    lastname = forms.CharField(
        # label='username',
        widget=forms.TextInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Lastname *'

            }
        )
    )
    email = forms.EmailField(

        # label='email',
        widget=forms.EmailInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Email *'

            }

        )
    )

    # @author Shubham
    # Date: April 20 2019

    # confirmmail = forms.EmailField(

    #     # label='email',
    #     widget=forms.EmailInput(

    #         attrs={
    #             # 'class': 'form-control',
    #             'placeholder': 'Confirm Email *'
    #         }

    #     )
    # )
    # ends here ~ @author Shubham

    password = forms.CharField(

        # label='Password',
        widget=forms.PasswordInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Password *'

            }
        )
    )
    reenter_password = forms.CharField(

        # label='Re-enter password',
        widget=forms.PasswordInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Re-enter password *'

            }
        )
    )

    def clean_username(self):
        un = self.cleaned_data['username']
        if len(un) <= 0:
            raise forms.ValidationError('enter a valid username')
        return un

    def clean_email(self):
        el = self.cleaned_data['email']
        if not re.match(r'\S+@\S+', el):
            raise forms.ValidationError('enter a valid email')
        return el
    # def clean(self):
    #     p1 = self.cleaned_data['password']
    #     p2 = self.cleaned_data['reenter_password']
    #     if  not (p1 == p2) :
    #         raise  forms.ValidationError('passwords are not matching')
    #     return p1 and p2


class RegistrationForm(forms.Form):
    # mobile = forms.IntegerField(
    #     widget= forms.NumberInput(
    #         attrs={
    #             'class':'form-control',
    #             'placeholder':'Mobile number *'
    #         }
    #
    #     )
    # )
    # location = forms.ChoiceField(choices=LOCATION__CHOICES)

    # @author Shubham
    # Date: April 20 2019

    location = forms.ChoiceField(choices=LOCATION__CHOICES)

    # location = forms.CharField(

    #     # label='Re-enter password',
    #     widget=forms.TextInput(

    #         attrs={
    #             # 'class': 'form-control',
    #             'placeholder': 'Location *'

    #         }
    #     )
    # )

    # gender = forms.ChoiceField(choices=GENDER__CHOICES)
    # ends here ~ @author Shubham


'''
class UserForm(forms.Form):

    firstname = forms.CharField(
        # label='username',
        widget=forms.TextInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Firstname *'

            }
        )
    )
    lastname = forms.CharField(
        # label='username',
        widget=forms.TextInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Lastname *'

            }
        )
    )
    email = forms.EmailField(

        # label='email',
        widget=forms.EmailInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Email *'

            }

        )
    )
    confirmmail = forms.EmailField(

        # label='email',
        widget=forms.EmailInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Confirm Email *'
            }

        )
    )
    password = forms.CharField(

        # label='Password',
        widget=forms.PasswordInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Password *'

            }
        )
    )
    reenter_password = forms.CharField(

        # label='Re-enter password',
        widget=forms.PasswordInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Re-enter password *'

            }
        )
    )
    def clean_username(self):
        un  = self.cleaned_data['username']
        if len(un) <= 0 :
            raise forms.ValidationError('enter a valid username')
        return un
    def clean_email(self):
        el = self.cleaned_data['email']
        if  not re.match(r'\S+@\S+', el):
            raise forms.ValidationError('enter a valid email')
        return el
    # def clean(self):
    #     p1 = self.cleaned_data['password']
    #     p2 = self.cleaned_data['reenter_password']
    #     if  not (p1 == p2) :
    #         raise  forms.ValidationError('passwords are not matching')
    #     return p1 and p2


class RegistrationForm(forms.Form):
    # mobile = forms.IntegerField(
    #     widget= forms.NumberInput(
    #         attrs={
    #             'class':'form-control',
    #             'placeholder':'Mobile number *'
    #         }
    #
    #     )
    # )
    # location = forms.ChoiceField(choices=LOCATION__CHOICES)
    location = forms.CharField(

        # label='Re-enter password',
        widget=forms.TextInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Location *'

            }
        )
    )
    gender = forms.ChoiceField(choices=GENDER__CHOICES)

'''


class LoginForm(forms.Form):
    email = forms.EmailField(
        # label='email',
        widget=forms.EmailInput(
            attrs={
                # 'class': 'form-control',
                'placeholder': 'Email *'
            }
        )
    )
    password = forms.CharField(

        # label='password',
        widget=forms.PasswordInput(

            attrs={
                # 'class': 'form-control',
                'placeholder': 'Password *'

            }
        ),
    )

    def clean_username(self):
        un = self.cleaned_data['username']
        if len(un) <= 0:
            raise forms.ValidationError('enter a valid username')
        return un

    def clean_password(self):
        ps = self.cleaned_data['password']
        if len(ps) <= 0:
            raise forms.ValidationError('enter password')
        return ps


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        # label='email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email *'

            }
        )
    )

    def clean_email(self):
        el = self.cleaned_data['email']
        if not re.match(r'\S+@\S+', el):
            raise forms.ValidationError('enter a valid email')
        return el


class ResetPassword(forms.Form):
    email = forms.EmailField(
        # label='email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email *'

            }
        )
    )
    password = forms.CharField(
        # label='username',
        widget=forms.PasswordInput(

            attrs={
                'class': 'form-control',
                'placeholder': 'Password *'

            }
        )
    )
    rpassword = forms.CharField(

        # label='password',
        widget=forms.PasswordInput(

            attrs={
                'class': 'form-control',
                'placeholder': 'Re enter password *'

            }
        ),
    )

    def clean_email(self):
        el = self.cleaned_data['email']
        if not re.match(r'\S+@\S+', el):
            raise forms.ValidationError('enter a valid email')
        return el

    def clean(self):
        ps = self.cleaned_data['password']
        rps = self.cleaned_data['rpassword']
        if len(ps) <= 0:
            raise forms.ValidationError('enter password !')
        elif ps != rps:
            raise forms.ValidationError('passwords not matching !')
        return ps


class ContactForm(forms.Form):
    name = forms.CharField(
        # label='username',
        widget=forms.TextInput(

            attrs={
                'class': 'form-control',
                'placeholder': 'Name *'

            }
        )
    )
    email = forms.EmailField(

        # label='email',
        widget=forms.EmailInput(

            attrs={
                'class': 'form-control',
                'placeholder': 'Email *'

            }

        )
    )
    mobile = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Mobile number *'
            }

        )
    )
    purpose = forms.ChoiceField(choices=PURPOSE__CHOICES)
    comment = comment = forms.CharField(widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'placeholder': 'Your message *'
        }
    ))


class LegalForm(forms.Form):

    gstin = forms.CharField(max_length=15, label="GSTIN Number",
                            widget=forms.TextInput(
                                attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Enter your 15 digit GSTIN number'

                                }
                            )
                            )

    pan = forms.CharField(max_length=10, label='PAN Number',
                          widget=forms.TextInput(
                              attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Enter your 10 digit PAN number'
                              }
                          )
                          )

    cin = forms.CharField(max_length=21, label='CIN Number',
                          widget=forms.TextInput(
                              attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Enter your 21 digits CIN number'
                              }
                          )
                          )

    gst_file = forms.FileField(label='GST Certificate (.pdf)',
                               widget=forms.FileInput(
                                   attrs={
                                       'class': 'form-control'
                                   }
                               )
                               )

    service_file = forms.FileField(label='Service agreement',
                                   widget=forms.FileInput(
                                       attrs={
                                           'class': 'form-control'
                                       }
                                   )
                                   )

    def clean_gstin(self):
        gst = self.cleaned_data.get('gstin')
        if len(gst) != 15:
            raise forms.ValidationError(
                'input your correct 15 digits GSTIN number')
        if gst[:2].isdigit() == False:
            raise forms.ValidationError('the 1st two digits should be numeric')
        return gst

    def clean_pan(self):
        pan = self.cleaned_data.get('pan')
        if len(pan) != 10:
            raise forms.ValidationError(
                'input your correct 10 digits PAN number')
        return pan

    def clean_cin(self):
        cin = self.cleaned_data.get('cin')
        if len(cin) != 21:
            raise forms.ValidationError(
                'input your correct 21 digits CIN number')

    def clean(self):
        gst = self.cleaned_data('gstin')
        pan = self.cleaned_data('pan')
        if not pan in gst:
            raise forms.ValidationError(
                'your PAN number is not in your GSTIN number')


############################################################################################
class UpdateContact(forms.Form):
    mobile = forms.IntegerField(
        label=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Mobile number *'
            }

        )
    )

    def clean(self):
        el = self.cleaned_data['mobile']
        if not re.match(r'^[0-9]+[0-9]+[0-9]+[0-9]+[0-9]+[0-9]+[0-9]+[0-9]+[0-9]+[0-9]$', str(el)):
            raise forms.ValidationError('enter a valid mobile no.')
        return el
###########################################################################################


    # @author Shubham
    # Date: April 20 2019

    # confirmmail = forms.EmailField(

    #     # label='email',
    #     widget=forms.EmailInput(

    #         attrs={
    #             # 'class': 'form-control',
    #             'placeholder': 'Confirm Email *'
    #         }

    #     )
    # )
    # ends here ~ @author Shubham
