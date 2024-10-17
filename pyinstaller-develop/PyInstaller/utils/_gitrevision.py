#
# The content of this file will be filled in with meaningful data when creating an archive using `git archive` or by
# downloading an archive from github, e.g., from github.com/.../archive/develop.zip
#
rev = "86cfc103ff"  # abbreviated commit hash
commit = "86cfc103ff29eca938d5c07c5db65c417eae5b47"  # commit hash
date = "2024-08-10 00:20:33 +0200"  # commit date
author = "Rok Mandeljc <rok.mandeljc@gmail.com>"
ref_names = "HEAD -> develop"  # incl. current branch
commit_message = """hookutils: Tcl/Tk: fix Tk data directory when using Tk framework bundle

On macOS, python 3.13.0rc1 build provides Tcl and Tk as private
framework bundles, located under
`/Library/Frameworks/Python.framework/Versions/3.13/Frameworks`.
Consequently, the Tcl and Tk script/data directories are
`[...]/Tcl.framework/Version/8.6/Resources/Scripts`
and
`[...]/Tk.framework/Versions/8.6/Resources/Scripts`,
respectively.

Therefore, `$tcl_root/../tkX.Y` does not apply, and we need to
infer location of the Tk data directory from the shared library
location.
"""
