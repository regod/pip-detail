import os
import pkg_resources
from pip.basecommand import Command
from pip.log import logger

class DetailCommand(Command):
    name = 'detail'
    usage = '%prog PkgName'
    summary = 'Output detail include relation pacakge'

    def __init__(self):
        super(DetailCommand, self).__init__()
        self.parser.add_option(
            '-f', '--files',
            dest='files',
            action='store_true',
            default=False,
            help='Show the full list of installed files for each package'
        )

    def run(self, options, args):
        if not args:
            logger.warn('ERROR: Please provide a project name or names.')
            return
        query = args

        results = search_packages_info(query)
        print_results(results, options.files)


def generic_dependences():
    dependences = {}
    for dist in pkg_resources.working_set:
        key = dist.project_name.lower()
        if key not in dependences:
            dependences[key] = []
        reqs = dist.requires()
        for req in reqs:
            key = req.project_name.lower()
            if key in dependences:
                dependences[key].append(dist.project_name)
            else:
                dependences[key] = [dist.project_name]
    return dependences

def search_packages_info(query):
    """
    Gather details from installed distributions. Print distribution name,
    version, location, and installed files. Installed files requires a
    pip generated 'installed-files.txt' in the distributions '.egg-info'
    directory.
    """
    dependences = generic_dependences()
    installed_packages = dict(
        [(p.project_name.lower(), p) for p in pkg_resources.working_set])
    for name in query:
        normalized_name = name.lower()
        if normalized_name in installed_packages:
            dist = installed_packages[normalized_name]
            relats = dependences[normalized_name]
            package = {
                'name': dist.project_name,
                'version': dist.version,
                'location': dist.location,
                'requires': [dep.project_name for dep in dist.requires()],
                'relation': [proj_name for proj_name in relats],
            }
            filelist = os.path.join(
                       dist.location,
                       dist.egg_name() + '.egg-info',
                       'installed-files.txt')
            if os.path.isfile(filelist):
                package['files'] = filelist
            yield package


def print_results(distributions, list_all_files):
    """
    Print the informations from installed distributions found.
    """
    for dist in distributions:
        logger.notify("---")
        logger.notify("Name: %s" % dist['name'])
        logger.notify("Version: %s" % dist['version'])
        logger.notify("Location: %s" % dist['location'])
        logger.notify("Requires: %s" % ', '.join(dist['requires']))
        logger.notify("Relation: %s" % ', '.join(dist['relation']))
        if list_all_files:
            logger.notify("Files:")
            if 'files' in dist:
                for line in open(dist['files']):
                    logger.notify("  %s" % line.strip())
            else:
                logger.notify("Cannot locate installed-files.txt")


DetailCommand()

