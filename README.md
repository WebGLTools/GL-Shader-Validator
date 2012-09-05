# GLShaderValidator

This is a [Sublime Text 2](http://www.sublimetext.com/) plugin that passes GLSL / ESSL to ANGLE's
preprocessor / compiler for validation.
Any errors that ANGLE finds are routed back to Sublime and the tokens in
the shader are highlighted for your convenience and debugging joy.
To see the details of the error check the status message in the bottom left of the
Sublime view.

## Installation

Right now you need to clone this repo into your packages folder
(typically ~/Library/Application Support/Sublime Text 2/Packages).

```
cd ~/Library/Application Support/Sublime Text 2/Packages
git clone git://github.com/WebGLTools/GL-Shader-Validator.git
```

Once we get out of alpha we will make this available via Package Control.

## Usage

Assuming that you have a [GLSL / ESSL syntax highlighter](https://github.com/euler0/sublime-glsl) installed in Sublime, all you should need to do
is install the plugin and your shader code will be validated as expected.

It's worth saying that ANGLE expects vertex shaders to have the file
suffix `.vert` and fragment shaders `.frag`. If you do not name your files
with that suffix ANGLE (and therefore the plugin) will not be able
to validate your shaders. Sadness will ensue.

## Permissions

This plugin requires use of a command line utility called essl_to_glsl, which is bundled with the plugin. By default,
however, the utility will not have execute permissions. The plugin will attempt to enable those permissions automatically when it loads, but
should that fail you will receive the following error message:

> GLShaderValidator: permission denied to use essl_to_glsl command

In such instances you should enable execute permissions yourself:

```
cd ~/Library/Application Support/Sublime Text 2/Packages/GLShaderValidator
chmod +x essl_to_glsl
```

## Settings

You can modify the settings file (`GLShaderValidator.sublime-settings`) inside
the plugin folder. You will find the documentation for the settings in
that file. There aren't many of those right now, but if you want more let us
know via the repo's Issues.

## Credits

* [Paul Lewis](http://aerotwist.com) - Pinky
* [Brendan Kenny](http://extremelysatisfactorytotalitarianism.com/) - The Brain
