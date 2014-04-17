import sublime
import sublime_plugin
import re
import subprocess
import os


class GLShaderError:
    """ Represents an error """
    region = None
    message = ''

    def __init__(self, region, message):
        self.region = region
        self.message = message


class ANGLECommandLine:
    """ Wrapper for ANGLE CLI """

    packagePath = "GL Shader Validator"
    platform = sublime.platform()
    errorPattern = re.compile("ERROR: 0:(\d+): '([^\']*)' : (.*)")
    permissionChecked = False
    ANGLEPath = {
        "osx": "./essl_to_glsl_osx",
        "linux": "./essl_to_glsl_linux",
        "windows": "essl_to_glsl_win.exe"
    }

    def ensure_script_permissions(self):
        """ Ensures that we have permission to execute the command """

        if not self.permissionChecked:
            os.chmod(sublime.packages_path() + os.sep + self.packagePath + os.sep + self.ANGLEPath[self.platform], 0o755)

        self.permissionChecked = True
        return self.permissionChecked

    def validate_contents(self, view):
        """ Validates the file contents using ANGLE """
        ANGLEPath = self.ANGLEPath[self.platform]
        errors = []
        fileLines = view.lines(
            sublime.Region(0, view.size())
        )

        specCmd = ''

        # NOTE: view.find is documented to return None if not found in ST2 and
        # ST3, but actually returns (-1, -1) in ST3

        # Go with WebGL spec
        inline_spec = view.find("spec: webgl", sublime.IGNORECASE)
        if view.settings().get('glsv_spec') == 0 or (inline_spec is not None and not inline_spec.empty()):
            specCmd = '-s=w'

        # Check if the user has changed which spec they
        # want to use. If they have, drop the switch
        inline_spec = view.find("spec: es2", sublime.IGNORECASE)
        if view.settings().get('glsv_spec') == 1 or (inline_spec is not None and not inline_spec.empty()):
            specCmd = ''

        inline_spec = view.find("spec: css", sublime.IGNORECASE)
        if view.settings().get('glsv_spec') == 2 or (inline_spec is not None and not inline_spec.empty()):
            specCmd = '-s=c'

        # We need an extra flag for windows
        if self.platform == "windows":
            specCmd = specCmd + " -b=h"

        # Create a shell process for essl_to_glsl and pick
        # up its output directly
        ANGLEProcess = subprocess.Popen(
            ANGLEPath + ' ' + specCmd + ' "' + view.file_name() + '"',
            cwd=sublime.packages_path() + os.sep + self.packagePath + os.sep,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True)

        if ANGLEProcess.stdout is not None:
            errlines = ANGLEProcess.stdout.readlines()

            # Go through each error, ignoring any comments
            for e in errlines:

                e = e.decode("utf-8")

                # Check if there was a permission denied
                # error running the essl_to_glsl cmd

                if re.search("permission denied", str(e), flags=re.IGNORECASE):
                    sublime.error_message("GLShaderValidator: permission denied to use essl_to_glsl command")
                    return []

                # ignore ANGLE's comments
                if not re.search("^####", e):

                    # Break down the error using the regexp
                    errorDetails = self.errorPattern.match(e)

                    # For each match construct an error
                    # object to pass back
                    if errorDetails is not None:
                        errorLine = int(errorDetails.group(1)) - 1
                        errorToken = errorDetails.group(2)
                        errorDescription = errorDetails.group(3)
                        errorLocation = fileLines[errorLine]

                        # If there is a token try and locate it
                        if len(errorToken) > 0:
                            betterLocation = view.find(
                                errorToken,
                                errorLocation.begin(),
                                sublime.LITERAL)

                            # Ensure we have a match before we
                            # replace the error region
                            if betterLocation is not None and not betterLocation.empty():
                                errorLocation = betterLocation

                        errors.append(GLShaderError(
                            errorLocation,
                            errorDescription
                        ))

        return errors


class GLShaderValidatorCommand(sublime_plugin.EventListener):
    """ Main Validator Class """
    ANGLECLI = ANGLECommandLine()
    errors = None
    loadedSettings = False
    pluginSettings = None

    # these are the default settings. They are overridden and
    # documented in the GLShaderValidator.sublime-settings file
    DEFAULT_SETTINGS = {
        "glsv_enabled": 1,
        "glsv_spec": 0
    }

    def __init__(self):
        """ Startup """

    def clear_settings(self):
        """ Resets the settings value so we will overwrite on the next run """
        for window in sublime.windows():
            for view in window.views():
                if view.settings().get('glsv_configured') is not None:
                    view.settings().set('glsv_configured', None)

    def apply_settings(self, view):
        """ Applies the settings from the settings file """

        # load in the settings file
        if self.pluginSettings is None:
            self.pluginSettings = sublime.load_settings(__name__ + ".sublime-settings")
            self.pluginSettings.clear_on_change('glsv_validator')
            self.pluginSettings.add_on_change('glsv_validator', self.clear_settings)

        if view.settings().get('glsv_configured') is None:

            view.settings().set('glsv_configured', True)

            # Go through the default settings
            for setting in self.DEFAULT_SETTINGS:

                # set the value
                settingValue = self.DEFAULT_SETTINGS[setting]

                # check if the user has overwritten the value
                # and switch to that instead
                if self.pluginSettings.get(setting) is not None:
                    settingValue = self.pluginSettings.get(setting)

                view.settings().set(setting, settingValue)

    def clear_errors(self, view):
        """ Removes any errors """
        view.erase_regions('glshadervalidate_errors')

    def is_glsl_or_essl(self, view):
        """ Checks that the file is GLSL or ESSL """
        syntax = view.settings().get('syntax')
        isShader = False
        if syntax is not None:
            isShader = re.search('GLSL|ESSL', syntax, flags=re.IGNORECASE) is not None
        return isShader

    def is_valid_file_ending(self, view):
        """ Checks that the file ending will work for ANGLE """
        isValidFileEnding = re.search('(frag|vert)$', view.file_name()) is not None
        return isValidFileEnding

    def show_errors(self, view):
        """ Passes over the array of errors and adds outlines """

        # Go through the errors that came back
        errorRegions = []
        for error in self.errors:
            errorRegions.append(error.region)

        # Put an outline around each one and a dot on the line
        view.add_regions(
            'glshadervalidate_errors',
            errorRegions,
            'glshader_error',
            'dot',
            sublime.DRAW_OUTLINED
        )

    def on_selection_modified(self, view):
        """ Shows a status message for an error region """

        view.erase_status('glshadervalidator')

        # If we have errors just locate
        # the first one and go with that for the status
        if self.is_glsl_or_essl(view) and self.errors is not None:
            for sel in view.sel():
                for error in self.errors:
                    if error.region.contains(sel):
                        view.set_status('glshadervalidator', error.message)
                        return

    def on_load(self, view):
        """ File loaded """
        self.run_validator(view)

    def on_activated(self, view):
        """ File activated """
        self.run_validator(view)

    def on_post_save(self, view):
        """ File saved """
        self.run_validator(view)

    def run_validator(self, view):
        """ Runs a validation pass """

        # clear the last run
        view.erase_status('glshadervalidator')

        # set up the settings if necessary
        self.apply_settings(view)

        # early return if they have disabled the linter
        if view.settings().get('glsv_enabled') == 0:
            self.clear_errors(view)
            return

        # early return for anything not syntax
        # highlighted as GLSL / ESSL
        if not self.is_glsl_or_essl(view):
            return

        # ANGLE expects files to be suffixed as .frag or
        # .vert so we need to do that check here
        if self.is_valid_file_ending(view):

            # Clear the last set of errors
            self.clear_errors

            # ensure that the script has permissions to run
            # this only runs once and is short circuited on subsequent calls
            self.ANGLECLI.ensure_script_permissions()

            # Get the file and send to ANGLE
            self.errors = self.ANGLECLI.validate_contents(view)
            self.show_errors(view)
        else:
            view.set_status('glshadervalidator', "File name must end in .frag or .vert")
