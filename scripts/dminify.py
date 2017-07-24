"""Create smaller sample from a dataset."""

import os
import gzip
import errno

import click
import dtoolcore


dataset_path_option = click.argument(
    'dataset_path',
    type=click.Path(exists=True))


def mkdir_parents(path):
    """Create the given directory path.
    This includes all necessary parent directories. Does not raise an error if
    the directory already exists.
    :param path: path to create
    """

    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def is_file_extension_in_list(filename, extension_list):
    for extension in extension_list:
        if filename.endswith(extension):
            return True

    return False


def minify(input_file, output_file, n=4000):

    print('minify from {} to {}'.format(input_file, output_file))

    output_dir = os.path.dirname(output_file)
    mkdir_parents(output_dir)
    with gzip.open(input_file, 'rb') as ifh:
        with gzip.open(output_file, 'wb') as ofh:
            for x in range(n):
                ofh.write(ifh.readline())


@click.command()
@dataset_path_option
@click.argument('new_dataset_path')
def dminify(dataset_path, new_dataset_path):

    parent_dataset = dtoolcore.DataSet.from_path(dataset_path)

    output_dir, dataset_name = os.path.split(new_dataset_path)

    # There are ways of doing this that result in error messages where
    # the specific offending argument is highlighted.
    # http://click.pocoo.org/5/options/#callbacks-for-validation
    if os.path.exists(new_dataset_path):
        raise click.BadParameter(
            "Path already exists: {}".format(new_dataset_path)
        )
    if not os.path.isdir(output_dir):
        raise click.BadParameter(
            "Output directory does not exist: {}".format(output_dir)
        )

    output_dataset_data_dir = os.path.join(new_dataset_path, 'data')

    for entry in parent_dataset.manifest['file_list']:
        if is_file_extension_in_list(entry['path'], ['.fq', '.fq.gz']):
            output_file_path = os.path.join(
                output_dataset_data_dir,
                entry['path']
            )
            identifier = entry['hash']
            input_file_path = parent_dataset.abspath_from_identifier(
                identifier
            )
            minify(input_file_path, output_file_path)

    output_dataset = dtoolcore.DataSet(dataset_name, 'data')
    output_dataset.persist_to_path(new_dataset_path)
    output_dataset.update_manifest()

    with open(parent_dataset.abs_readme_path, 'r') as ifh:
        with open(output_dataset.abs_readme_path, 'w') as ofh:
            ofh.write(ifh.read())
            ofh.write("minified_from: {}\n".format(parent_dataset.uuid))

if __name__ == '__main__':
    dminify()
