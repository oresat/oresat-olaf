from setuptools import setup

setup(
    package_data={
        'olaf': ['data/*']
    },
    entry_points={
        'console_scripts': [
            'olaf-sdo-transfer = olaf.scripts.sdo_transfer:main',
            'olaf-file-transfer = olaf.scripts.file_transfer:main',
            'olaf-os-command = olaf.scripts.os_command:main',
            'olaf-system-info = olaf.scripts.system_info:main',
        ],
    },
)
