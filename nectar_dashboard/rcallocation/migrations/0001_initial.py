from django.db import migrations, models
import datetime
import django.core.validators
import nectar_dashboard.rcallocation.models


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='AllocationRequest',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        default=b'N',
                        max_length=1,
                        choices=[
                            (b'N', b'New'),
                            (b'E', b'Submitted'),
                            (b'A', b'Approved'),
                            (b'R', b'Declined'),
                            (b'X', b'Update/extension requested'),
                            (b'J', b'Update/extension declined'),
                            (b'P', b'Provisioned'),
                            (b'L', b'Legacy submission'),
                            (b'M', b'Legacy approved'),
                            (b'O', b'Legacy rejected'),
                        ],
                    ),
                ),
                (
                    'status_explanation',
                    models.TextField(
                        help_text=b'A brief explanation of the reason the request has been sent back to the user for changes',
                        null=True,
                        verbose_name=b'Reason',
                        blank=True,
                    ),
                ),
                ('created_by', models.CharField(max_length=100)),
                (
                    'submit_date',
                    models.DateField(
                        default=datetime.date.today,
                        verbose_name=b'Submission Date',
                    ),
                ),
                (
                    'modified_time',
                    models.DateTimeField(
                        default=datetime.datetime.utcnow,
                        verbose_name=b'Modified Date',
                    ),
                ),
                (
                    'tenant_name',
                    models.CharField(
                        help_text=b'A short name used to identify your project.<br>Must contain only letters and numbers.<br>16 characters max.',
                        max_length=64,
                        null=True,
                        verbose_name=b'Project identifier',
                        blank=True,
                    ),
                ),
                (
                    'project_name',
                    models.CharField(
                        help_text=b'A human-friendly descriptive name for your research project.',
                        max_length=200,
                        verbose_name=b'Project allocation title',
                    ),
                ),
                (
                    'contact_email',
                    models.EmailField(
                        help_text=b'The e-mail address provided by your IdP which\n                     will be used to communicate with you about this\n                     allocation request.  <strong>Note:</strong> <i>if\n                     this is not a valid e-mail address you will not\n                     receive communications on any allocation request\n                     you make</i>. If invalid please contact your IdP\n                     and ask them to correct your e-mail address!',
                        max_length=254,
                        verbose_name=b'Contact e-mail',
                        blank=True,
                    ),
                ),
                (
                    'start_date',
                    models.DateField(
                        default=datetime.date.today,
                        help_text=b'The day on which you want your Project Allocation to\n                     go live. Format: yyyy-mm-dd',
                        verbose_name=b'Start date',
                    ),
                ),
                (
                    'end_date',
                    models.DateField(
                        default=nectar_dashboard.rcallocation.models._six_months_from_now,
                        help_text=b'The day on which your project will end.',
                        verbose_name=b'Estimated end date',
                        editable=False,
                    ),
                ),
                (
                    'estimated_project_duration',
                    models.IntegerField(
                        default=1,
                        help_text=b'Resources are approved for at most 12-months,\n                    but projects can extend a request for resources\n                    once it has been approved.',
                        verbose_name=b'Estimated project duration',
                        choices=[
                            (1, b'1-month'),
                            (3, b'3-months'),
                            (6, b'6-months'),
                            (12, b'12-months'),
                        ],
                    ),
                ),
                (
                    'convert_trial_project',
                    models.BooleanField(
                        default=False,
                        help_text=b'If selected, your existing trial project pt- will be renamed so any resources inside it will become part of this new allocation. A new trial project will be created in its place.',
                        verbose_name=b'Convert trial project?',
                    ),
                ),
                (
                    'primary_instance_type',
                    models.CharField(
                        default=b' ',
                        help_text=b'\n        This is the typical VM size you expect to use. Five basic\n        types of primary instance are available:\n        <table class="text-left table-condensed">\n          <tr><th>Name</th><th>VCPUs</th><th>RAM</th><th>Local Disk</th></tr>\n          <tr><td><b>m1.small</b></td><td>1</td><td>4GB</td><td>30GB</td></tr>\n          <tr>\n              <td><b>m1.medium</b></td><td>2</td><td>8GB</td><td>60GB</td>\n          </tr>\n          <tr>\n              <td><b>m1.large</b></td><td>4</td><td>16GB</td><td>120GB</td>\n          </tr>\n          <tr>\n              <td><b>m1.xlarge</b></td><td>8</td><td>32GB</td><td>240GB</td>\n          </tr>\n          <tr>\n              <td><b>m1.xxlarge</b></td><td>16</td><td>64GB</td><td>480GB</td>\n          </tr>\n        </table>\n\n        Compute resources are subject to availability and from time to\n        time some flavors will not be available.  It is recommended\n        that you consider using 4 and 2 core instances to distribute\n        your work load.\n        ',
                        max_length=1,
                        blank=True,
                        choices=[
                            (b'S', b'm1.small'),
                            (b'M', b'm1.medium'),
                            (b'B', b'm1.large'),
                            (b'L', b'm1.xlarge'),
                            (b'X', b'm1.xxlarge'),
                        ],
                    ),
                ),
                (
                    'instances',
                    models.IntegerField(
                        default=2,
                        help_text=b'The maximum number of instances that you think your project will require at any one time.',
                        verbose_name=b'Number of instances',
                    ),
                ),
                (
                    'cores',
                    models.IntegerField(
                        default=2,
                        help_text=b'This is the maximum number of cores you\'d\n                    like to use at any one time across all instances.\n                    For example, if you\'d like to be able to run two\n                    "XXL Sized" instances at once (each has 16 CPU cores),\n                    you should specify 32 here.',
                        verbose_name=b'Number of cores',
                    ),
                ),
                (
                    'core_hours',
                    models.IntegerField(
                        default=744,
                        help_text=b'<p>\n                    Core hours is the number of hours multiplied by the\n                    number of cores in use. The default value in this field\n                    is half of the core hours required to run all of the\n                    cores requested over the estimated project period.\n                    This should be adjusted up or down as required.\n                    </p>\n                     For example:\n                     <ul>\n                       <li>\n                           * A 1-core Virtual Machine will use 24 core hours\n                           each day it is used\n                       </li>\n                       <li>\n                           * A 2-core Virtual Machine will use 48 core hours\n                           each day it is used\n                       </li>\n                       <li>\n                           * A 4-core Virtual Machine will use 96 core hours\n                           each day it is used\n                       </li>\n                       <li>\n                           * A 8-core Virtual Machine will use 192 core hours\n                           each day it is used\n                       </li>\n                     </ul>\n                     ',
                        verbose_name=b'Number of core hours',
                    ),
                ),
                (
                    'instance_quota',
                    models.IntegerField(
                        default=b'0', verbose_name=b'Instance count quota'
                    ),
                ),
                (
                    'ram_quota',
                    models.IntegerField(
                        default=b'0', verbose_name=b'Maximum RAM usage quota'
                    ),
                ),
                (
                    'core_quota',
                    models.IntegerField(
                        default=b'0',
                        verbose_name=b'Maximum number of cores available',
                    ),
                ),
                (
                    'approver_email',
                    models.EmailField(
                        max_length=254,
                        verbose_name=b'Approver email',
                        blank=True,
                    ),
                ),
                (
                    'volume_zone',
                    models.CharField(
                        default=b'',
                        max_length=64,
                        blank=True,
                        help_text=b'Optional. Select a location here if you need volumes\n                     located at a specific node.',
                        null=True,
                        verbose_name=b'Persistent Volume location',
                    ),
                ),
                (
                    'object_storage_zone',
                    models.CharField(
                        default=b'',
                        max_length=64,
                        blank=True,
                        help_text=b'Optional. Select a location here if you need\n                     object storage located at a specific node.',
                        null=True,
                        verbose_name=b'Object Storage location',
                    ),
                ),
                (
                    'use_case',
                    models.TextField(
                        help_text=b'A short write up on how you intend to to use your\n        cloud instances will help us in our decision making.',
                        max_length=4096,
                        verbose_name=b'Research use case',
                    ),
                ),
                (
                    'usage_patterns',
                    models.TextField(
                        help_text=b'Will your project have many users and small data\n                sets? Or will it have large data sets with a small\n                number of users? Your answers here will help us.',
                        max_length=1024,
                        verbose_name=b'Instance, Object Storage and Volumes Storage Usage Patterns',
                        blank=True,
                    ),
                ),
                (
                    'allocation_home',
                    models.CharField(
                        default=b'national',
                        help_text=b'You can provide a primary location where you expect to\n                use most resources, effectively the main NeCTAR node for your\n                allocation. Use of other locations is still possible.\n                This can also indicate a specific arrangement with a\n                NeCTAR Node, for example where you obtain support, or if\n                your institution is a supporting member of that Node.\n                ',
                        max_length=128,
                        verbose_name=b'Allocation home location',
                        choices=[
                            (b'national', b'National/Unassigned'),
                            (b'nci', b'Australian Capital Territory (NCI)'),
                            (b'intersect', b'New South Wales (Intersect)'),
                            (b'qcif', b'Queensland (QCIF)'),
                            (b'ersa', b'South Australia (eRSA)'),
                            (b'tpac', b'Tasmania (TPAC)'),
                            (b'uom', b'Victoria (Melbourne)'),
                            (b'monash', b'Victoria (Monash)'),
                            (b'pawsey', b'Western Australia (Pawsey)'),
                        ],
                    ),
                ),
                (
                    'geographic_requirements',
                    models.TextField(
                        help_text=b'Indicate to the allocations committee any special\n                geographic requirements that you may need?  Please note\n                that the ability to run virtual machines at specified\n                locations is normal functionality and not a\n                special requirement.',
                        max_length=1024,
                        verbose_name=b'Additional location requirements',
                        blank=True,
                    ),
                ),
                (
                    'tenant_uuid',
                    models.CharField(max_length=36, null=True, blank=True),
                ),
                (
                    'estimated_number_users',
                    models.IntegerField(
                        default=b'1',
                        help_text=b'Estimated number of users, researchers and collaborators\n        to be supported by the allocation.',
                        error_messages={
                            b'min_value': b'The estimated number of users must be great than 0'
                        },
                        verbose_name=b'Estimated number of users',
                        validators=[
                            django.core.validators.MinValueValidator(1)
                        ],
                    ),
                ),
                (
                    'field_of_research_1',
                    models.CharField(
                        blank=True,
                        max_length=6,
                        null=True,
                        verbose_name=b'First Field Of Research',
                        choices=[
                            (b'01', b'01 MATHEMATICAL SCIENCES'),
                            (b'0101', b'0101 PURE MATHEMATICS'),
                            (b'010101', b'010101 Algebra and Number Theory'),
                            (
                                b'010102',
                                b'010102 Algebraic and Differential Geometry',
                            ),
                            (
                                b'010103',
                                b'010103 Category Theory, K Theory, Homological Algebra',
                            ),
                            (
                                b'010104',
                                b'010104 Combinatorics and Discrete Mathematics (excl. Physical Combinatorics)',
                            ),
                            (
                                b'010105',
                                b'010105 Group Theory and Generalisations',
                            ),
                            (
                                b'010106',
                                b'010106 Lie Groups, Harmonic and Fourier Analysis',
                            ),
                            (
                                b'010107',
                                b'010107 Mathematical Logic, Set Theory, Lattices and Universal Algebra',
                            ),
                            (
                                b'010108',
                                b'010108 Operator Algebras and Functional Analysis',
                            ),
                            (
                                b'010109',
                                b'010109 Ordinary Differential Equations, Difference Equations and Dynamical Systems',
                            ),
                            (
                                b'010110',
                                b'010110 Partial Differential Equations',
                            ),
                            (
                                b'010111',
                                b'010111 Real and Complex Functions (incl. Several Variables)',
                            ),
                            (b'010112', b'010112 Topology'),
                            (
                                b'010199',
                                b'010199 Pure Mathematics not elsewhere classified',
                            ),
                            (b'0102', b'0102 APPLIED MATHEMATICS'),
                            (
                                b'010201',
                                b'010201 Approximation Theory and Asymptotic Methods',
                            ),
                            (b'010202', b'010202 Biological Mathematics'),
                            (
                                b'010203',
                                b'010203 Calculus of Variations, Systems Theory and Control Theory',
                            ),
                            (
                                b'010204',
                                b'010204 Dynamical Systems in Applications',
                            ),
                            (b'010205', b'010205 Financial Mathematics'),
                            (b'010206', b'010206 Operations Research'),
                            (
                                b'010207',
                                b'010207 Theoretical and Applied Mechanics',
                            ),
                            (
                                b'010299',
                                b'010299 Applied Mathematics not elsewhere classified',
                            ),
                            (
                                b'0103',
                                b'0103 NUMERICAL AND COMPUTATIONAL MATHEMATICS',
                            ),
                            (b'010301', b'010301 Numerical Analysis'),
                            (
                                b'010302',
                                b'010302 Numerical Solution of Differential and Integral Equations',
                            ),
                            (b'010303', b'010303 Optimisation'),
                            (
                                b'010399',
                                b'010399 Numerical and Computational Mathematics not elsewhere classified',
                            ),
                            (b'0104', b'0104 STATISTICS'),
                            (b'010401', b'010401 Applied Statistics'),
                            (b'010402', b'010402 Biostatistics'),
                            (b'010403', b'010403 Forensic Statistics'),
                            (b'010404', b'010404 Probability Theory'),
                            (b'010405', b'010405 Statistical Theory'),
                            (
                                b'010406',
                                b'010406 Stochastic Analysis and Modelling',
                            ),
                            (
                                b'010499',
                                b'010499 Statistics not elsewhere classified',
                            ),
                            (b'0105', b'0105 MATHEMATICAL PHYSICS'),
                            (
                                b'010501',
                                b'010501 Algebraic Structures in Mathematical Physics',
                            ),
                            (
                                b'010502',
                                b'010502 Integrable Systems (Classical and Quantum)',
                            ),
                            (
                                b'010503',
                                b'010503 Mathematical Aspects of Classical Mechanics, Quantum Mechanics and Quantum Information Theory',
                            ),
                            (
                                b'010504',
                                b'010504 Mathematical Aspects of General Relativity',
                            ),
                            (
                                b'010505',
                                b'010505 Mathematical Aspects of Quantum and Conformal Field Theory, Quantum Gravity and String Theory',
                            ),
                            (
                                b'010506',
                                b'010506 Statistical Mechanics, Physical Combinatorics and Mathematical Aspects of Condensed Matter',
                            ),
                            (
                                b'010599',
                                b'010599 Mathematical Physics not elsewhere classified',
                            ),
                            (b'0199', b'0199 OTHER MATHEMATICAL SCIENCES'),
                            (
                                b'019999',
                                b'019999 Mathematical Sciences not elsewhere classified',
                            ),
                            (b'02', b'02 PHYSICAL SCIENCES'),
                            (b'0201', b'0201 ASTRONOMICAL AND SPACE SCIENCES'),
                            (b'020101', b'020101 Astrobiology'),
                            (
                                b'020102',
                                b'020102 Astronomical and Space Instrumentation',
                            ),
                            (
                                b'020103',
                                b'020103 Cosmology and Extragalactic Astronomy',
                            ),
                            (b'020104', b'020104 Galactic Astronomy'),
                            (
                                b'020105',
                                b'020105 General Relativity and Gravitational Waves',
                            ),
                            (
                                b'020106',
                                b'020106 High Energy Astrophysics; Cosmic Rays',
                            ),
                            (
                                b'020107',
                                b'020107 Mesospheric, Ionospheric and Magnetospheric Physics',
                            ),
                            (
                                b'020108',
                                b'020108 Planetary Science (excl. Extraterrestrial Geology)',
                            ),
                            (b'020109', b'020109 Space and Solar Physics'),
                            (
                                b'020110',
                                b'020110 Stellar Astronomy and Planetary Systems',
                            ),
                            (
                                b'020199',
                                b'020199 Astronomical and Space Sciences not elsewhere classified',
                            ),
                            (
                                b'0202',
                                b'0202 ATOMIC, MOLECULAR, NUCLEAR, PARTICLE AND PLASMA PHYSICS',
                            ),
                            (
                                b'020201',
                                b'020201 Atomic and Molecular Physics',
                            ),
                            (b'020202', b'020202 Nuclear Physics'),
                            (b'020203', b'020203 Particle Physics'),
                            (
                                b'020204',
                                b'020204 Plasma Physics; Fusion Plasmas; Electrical Discharges',
                            ),
                            (
                                b'020299',
                                b'020299 Atomic, Molecular, Nuclear, Particle and Plasma Physics not elsewhere classified',
                            ),
                            (b'0203', b'0203 CLASSICAL PHYSICS'),
                            (
                                b'020301',
                                b'020301 Acoustics and Acoustical Devices; Waves',
                            ),
                            (
                                b'020302',
                                b'020302 Electrostatics and Electrodynamics',
                            ),
                            (b'020303', b'020303 Fluid Physics'),
                            (
                                b'020304',
                                b'020304 Thermodynamics and Statistical Physics',
                            ),
                            (
                                b'020399',
                                b'020399 Classical Physics not elsewhere classified',
                            ),
                            (b'0204', b'0204 CONDENSED MATTER PHYSICS'),
                            (
                                b'020401',
                                b'020401 Condensed Matter Characterisation Technique Development',
                            ),
                            (b'020402', b'020402 Condensed Matter Imaging'),
                            (
                                b'020403',
                                b'020403 Condensed Matter Modelling and Density Functional Theory',
                            ),
                            (
                                b'020404',
                                b'020404 Electronic and Magnetic Properties of Condensed Matter; Superconductivity',
                            ),
                            (b'020405', b'020405 Soft Condensed Matter'),
                            (
                                b'020406',
                                b'020406 Surfaces and Structural Properties of Condensed Matter',
                            ),
                            (
                                b'020499',
                                b'020499 Condensed Matter Physics not elsewhere classified',
                            ),
                            (b'0205', b'0205 OPTICAL PHYSICS'),
                            (
                                b'020501',
                                b'020501 Classical and Physical Optics',
                            ),
                            (
                                b'020502',
                                b'020502 Lasers and Quantum Electronics',
                            ),
                            (
                                b'020503',
                                b'020503 Nonlinear Optics and Spectroscopy',
                            ),
                            (
                                b'020504',
                                b'020504 Photonics, Optoelectronics and Optical Communications',
                            ),
                            (
                                b'020599',
                                b'020599 Optical Physics not elsewhere classified',
                            ),
                            (b'0206', b'0206 QUANTUM PHYSICS'),
                            (
                                b'020601',
                                b'020601 Degenerate Quantum Gases and Atom Optics',
                            ),
                            (
                                b'020602',
                                b'020602 Field Theory and String Theory',
                            ),
                            (
                                b'020603',
                                b'020603 Quantum Information, Computation and Communication',
                            ),
                            (b'020604', b'020604 Quantum Optics'),
                            (
                                b'020699',
                                b'020699 Quantum Physics not elsewhere classified',
                            ),
                            (b'0299', b'0299 OTHER PHYSICAL SCIENCES'),
                            (b'029901', b'029901 Biological Physics'),
                            (b'029902', b'029902 Complex Physical Systems'),
                            (b'029903', b'029903 Medical Physics'),
                            (
                                b'029904',
                                b'029904 Synchrotrons; Accelerators; Instruments and Techniques',
                            ),
                            (
                                b'029999',
                                b'029999 Physical Sciences not elsewhere classified',
                            ),
                            (b'03', b'03 CHEMICAL SCIENCES'),
                            (b'0301', b'0301 ANALYTICAL CHEMISTRY'),
                            (b'030101', b'030101 Analytical Spectrometry'),
                            (b'030102', b'030102 Electroanalytical Chemistry'),
                            (b'030103', b'030103 Flow Analysis'),
                            (
                                b'030104',
                                b'030104 Immunological and Bioassay Methods',
                            ),
                            (
                                b'030105',
                                b'030105 Instrumental Methods (excl. Immunological and Bioassay Methods)',
                            ),
                            (
                                b'030106',
                                b'030106 Quality Assurance, Chemometrics, Traceability and Metrological Chemistry',
                            ),
                            (
                                b'030107',
                                b'030107 Sensor Technology (Chemical aspects)',
                            ),
                            (b'030108', b'030108 Separation Science'),
                            (
                                b'030199',
                                b'030199 Analytical Chemistry not elsewhere classified',
                            ),
                            (b'0302', b'0302 INORGANIC CHEMISTRY'),
                            (b'030201', b'030201 Bioinorganic Chemistry'),
                            (b'030202', b'030202 f-Block Chemistry'),
                            (b'030203', b'030203 Inorganic Green Chemistry'),
                            (b'030204', b'030204 Main Group Metal Chemistry'),
                            (b'030205', b'030205 Non-metal Chemistry'),
                            (b'030206', b'030206 Solid State Chemistry'),
                            (b'030207', b'030207 Transition Metal Chemistry'),
                            (
                                b'030299',
                                b'030299 Inorganic Chemistry not elsewhere classified',
                            ),
                            (
                                b'0303',
                                b'0303 MACROMOLECULAR AND MATERIALS CHEMISTRY',
                            ),
                            (
                                b'030301',
                                b'030301 Chemical Characterisation of Materials',
                            ),
                            (
                                b'030302',
                                b'030302 Nanochemistry and Supramolecular Chemistry',
                            ),
                            (
                                b'030303',
                                b'030303 Optical Properties of Materials',
                            ),
                            (
                                b'030304',
                                b'030304 Physical Chemistry of Materials',
                            ),
                            (b'030305', b'030305 Polymerisation Mechanisms'),
                            (b'030306', b'030306 Synthesis of Materials'),
                            (
                                b'030307',
                                b'030307 Theory and Design of Materials',
                            ),
                            (
                                b'030399',
                                b'030399 Macromolecular and Materials Chemistry not elsewhere classified',
                            ),
                            (
                                b'0304',
                                b'0304 MEDICINAL AND BIOMOLECULAR CHEMISTRY',
                            ),
                            (
                                b'030401',
                                b'030401 Biologically Active Molecules',
                            ),
                            (
                                b'030402',
                                b'030402 Biomolecular Modelling and Design',
                            ),
                            (
                                b'030403',
                                b'030403 Characterisation of Biological Macromolecules',
                            ),
                            (
                                b'030404',
                                b'030404 Cheminformatics and Quantitative Structure-Activity Relationships',
                            ),
                            (b'030405', b'030405 Molecular Medicine'),
                            (b'030406', b'030406 Proteins and Peptides'),
                            (
                                b'030499',
                                b'030499 Medicinal and Biomolecular Chemistry not elsewhere classified',
                            ),
                            (b'0305', b'0305 ORGANIC CHEMISTRY'),
                            (b'030501', b'030501 Free Radical Chemistry'),
                            (b'030502', b'030502 Natural Products Chemistry'),
                            (b'030503', b'030503 Organic Chemical Synthesis'),
                            (b'030504', b'030504 Organic Green Chemistry'),
                            (b'030505', b'030505 Physical Organic Chemistry'),
                            (
                                b'030599',
                                b'030599 Organic Chemistry not elsewhere classified',
                            ),
                            (
                                b'0306',
                                b'0306 PHYSICAL CHEMISTRY (INCL. STRUCTURAL)',
                            ),
                            (
                                b'030601',
                                b'030601 Catalysis and Mechanisms of Reactions',
                            ),
                            (
                                b'030602',
                                b'030602 Chemical Thermodynamics and Energetics',
                            ),
                            (
                                b'030603',
                                b'030603 Colloid and Surface Chemistry',
                            ),
                            (b'030604', b'030604 Electrochemistry'),
                            (b'030605', b'030605 Solution Chemistry'),
                            (
                                b'030606',
                                b'030606 Structural Chemistry and Spectroscopy',
                            ),
                            (
                                b'030607',
                                b'030607 Transport Properties and Non-equilibrium Processes',
                            ),
                            (
                                b'030699',
                                b'030699 Physical Chemistry not elsewhere classified',
                            ),
                            (
                                b'0307',
                                b'0307 THEORETICAL AND COMPUTATIONAL CHEMISTRY',
                            ),
                            (b'030701', b'030701 Quantum Chemistry'),
                            (b'030702', b'030702 Radiation and Matter'),
                            (
                                b'030703',
                                b'030703 Reaction Kinetics and Dynamics',
                            ),
                            (
                                b'030704',
                                b'030704 Statistical Mechanics in Chemistry',
                            ),
                            (
                                b'030799',
                                b'030799 Theoretical and Computational Chemistry not elsewhere classified',
                            ),
                            (b'0399', b'0399 OTHER CHEMICAL SCIENCES'),
                            (
                                b'039901',
                                b'039901 Environmental Chemistry (incl. Atmospheric Chemistry)',
                            ),
                            (b'039902', b'039902 Forensic Chemistry'),
                            (b'039903', b'039903 Industrial Chemistry'),
                            (b'039904', b'039904 Organometallic Chemistry'),
                            (
                                b'039999',
                                b'039999 Chemical Sciences not elsewhere classified',
                            ),
                            (b'04', b'04 EARTH SCIENCES'),
                            (b'0401', b'0401 ATMOSPHERIC SCIENCES'),
                            (b'040101', b'040101 Atmospheric Aerosols'),
                            (b'040102', b'040102 Atmospheric Dynamics'),
                            (b'040103', b'040103 Atmospheric Radiation'),
                            (b'040104', b'040104 Climate Change Processes'),
                            (
                                b'040105',
                                b'040105 Climatology (excl. Climate Change Processes)',
                            ),
                            (b'040106', b'040106 Cloud Physics'),
                            (b'040107', b'040107 Meteorology'),
                            (
                                b'040108',
                                b'040108 Tropospheric and Stratospheric Physics',
                            ),
                            (
                                b'040199',
                                b'040199 Atmospheric Sciences not elsewhere classified',
                            ),
                            (b'0402', b'0402 GEOCHEMISTRY'),
                            (b'040201', b'040201 Exploration Geochemistry'),
                            (b'040202', b'040202 Inorganic Geochemistry'),
                            (b'040203', b'040203 Isotope Geochemistry'),
                            (b'040204', b'040204 Organic Geochemistry'),
                            (
                                b'040299',
                                b'040299 Geochemistry not elsewhere classified',
                            ),
                            (b'0403', b'0403 GEOLOGY'),
                            (b'040301', b'040301 Basin Analysis'),
                            (b'040302', b'040302 Extraterrestrial Geology'),
                            (b'040303', b'040303 Geochronology'),
                            (
                                b'040304',
                                b'040304 Igneous and Metamorphic Petrology',
                            ),
                            (b'040305', b'040305 Marine Geoscience'),
                            (
                                b'040306',
                                b'040306 Mineralogy and Crystallography',
                            ),
                            (b'040307', b'040307 Ore Deposit Petrology'),
                            (
                                b'040308',
                                b'040308 Palaeontology (incl. Palynology)',
                            ),
                            (b'040309', b'040309 Petroleum and Coal Geology'),
                            (b'040310', b'040310 Sedimentology'),
                            (
                                b'040311',
                                b'040311 Stratigraphy (incl. Biostratigraphy and Sequence Stratigraphy)',
                            ),
                            (b'040312', b'040312 Structural Geology'),
                            (b'040313', b'040313 Tectonics'),
                            (b'040314', b'040314 Volcanology'),
                            (
                                b'040399',
                                b'040399 Geology not elsewhere classified',
                            ),
                            (b'0404', b'0404 GEOPHYSICS'),
                            (
                                b'040401',
                                b'040401 Electrical and Electromagnetic Methods in Geophysics',
                            ),
                            (b'040402', b'040402 Geodynamics'),
                            (b'040403', b'040403 Geophysical Fluid Dynamics'),
                            (
                                b'040404',
                                b'040404 Geothermics and Radiometrics',
                            ),
                            (b'040405', b'040405 Gravimetrics'),
                            (
                                b'040406',
                                b'040406 Magnetism and Palaeomagnetism',
                            ),
                            (
                                b'040407',
                                b'040407 Seismology and Seismic Exploration',
                            ),
                            (
                                b'040499',
                                b'040499 Geophysics not elsewhere classified',
                            ),
                            (b'0405', b'0405 OCEANOGRAPHY'),
                            (b'040501', b'040501 Biological Oceanography'),
                            (b'040502', b'040502 Chemical Oceanography'),
                            (b'040503', b'040503 Physical Oceanography'),
                            (
                                b'040599',
                                b'040599 Oceanography not elsewhere classified',
                            ),
                            (
                                b'0406',
                                b'0406 PHYSICAL GEOGRAPHY AND ENVIRONMENTAL GEOSCIENCE',
                            ),
                            (
                                b'040601',
                                b'040601 Geomorphology and Regolith and Landscape Evolution',
                            ),
                            (b'040602', b'040602 Glaciology'),
                            (b'040603', b'040603 Hydrogeology'),
                            (b'040604', b'040604 Natural Hazards'),
                            (b'040605', b'040605 Palaeoclimatology'),
                            (b'040606', b'040606 Quaternary Environments'),
                            (b'040607', b'040607 Surface Processes'),
                            (b'040608', b'040608 Surfacewater Hydrology'),
                            (
                                b'040699',
                                b'040699 Physical Geography and Environmental Geoscience not elsewhere classified',
                            ),
                            (b'0499', b'0499 OTHER EARTH SCIENCES'),
                            (
                                b'049999',
                                b'049999 Earth Sciences not elsewhere classified',
                            ),
                            (b'05', b'05 ENVIRONMENTAL SCIENCES'),
                            (b'0501', b'0501 ECOLOGICAL APPLICATIONS'),
                            (
                                b'050101',
                                b'050101 Ecological Impacts of Climate Change',
                            ),
                            (b'050102', b'050102 Ecosystem Function'),
                            (b'050103', b'050103 Invasive Species Ecology'),
                            (b'050104', b'050104 Landscape Ecology'),
                            (
                                b'050199',
                                b'050199 Ecological Applications not elsewhere classified',
                            ),
                            (
                                b'0502',
                                b'0502 ENVIRONMENTAL SCIENCE AND MANAGEMENT',
                            ),
                            (
                                b'050201',
                                b'050201 Aboriginal and Torres Strait Islander Environmental Knowledge',
                            ),
                            (
                                b'050202',
                                b'050202 Conservation and Biodiversity',
                            ),
                            (
                                b'050203',
                                b'050203 Environmental Education and Extension',
                            ),
                            (
                                b'050204',
                                b'050204 Environmental Impact Assessment',
                            ),
                            (b'050205', b'050205 Environmental Management'),
                            (b'050206', b'050206 Environmental Monitoring'),
                            (
                                b'050207',
                                b'050207 Environmental Rehabilitation (excl. Bioremediation)',
                            ),
                            (
                                b'050208',
                                b'050208 Maori Environmental Knowledge',
                            ),
                            (b'050209', b'050209 Natural Resource Management'),
                            (
                                b'050210',
                                b'050210 Pacific Peoples Environmental Knowledge',
                            ),
                            (
                                b'050211',
                                b'050211 Wildlife and Habitat Management',
                            ),
                            (
                                b'050299',
                                b'050299 Environmental Science and Management not elsewhere classified',
                            ),
                            (b'0503', b'0503 SOIL SCIENCES'),
                            (
                                b'050301',
                                b'050301 Carbon Sequestration Science',
                            ),
                            (
                                b'050302',
                                b'050302 Land Capability and Soil Degradation',
                            ),
                            (b'050303', b'050303 Soil Biology'),
                            (
                                b'050304',
                                b'050304 Soil Chemistry (excl. Carbon Sequestration Science)',
                            ),
                            (b'050305', b'050305 Soil Physics'),
                            (
                                b'050399',
                                b'050399 Soil Sciences not elsewhere classified',
                            ),
                            (b'0599', b'0599 OTHER ENVIRONMENTAL SCIENCES'),
                            (
                                b'059999',
                                b'059999 Environmental Sciences not elsewhere classified',
                            ),
                            (b'06', b'06 BIOLOGICAL SCIENCES'),
                            (b'0601', b'0601 BIOCHEMISTRY AND CELL BIOLOGY'),
                            (b'060101', b'060101 Analytical Biochemistry'),
                            (b'060102', b'060102 Bioinformatics'),
                            (
                                b'060103',
                                b'060103 Cell Development, Proliferation and Death',
                            ),
                            (b'060104', b'060104 Cell Metabolism'),
                            (b'060105', b'060105 Cell Neurochemistry'),
                            (
                                b'060106',
                                b'060106 Cellular Interactions (incl. Adhesion, Matrix, Cell Wall)',
                            ),
                            (b'060107', b'060107 Enzymes'),
                            (b'060108', b'060108 Protein Trafficking'),
                            (
                                b'060109',
                                b'060109 Proteomics and Intermolecular Interactions (excl. Medical Proteomics)',
                            ),
                            (
                                b'060110',
                                b'060110 Receptors and Membrane Biology',
                            ),
                            (b'060111', b'060111 Signal Transduction'),
                            (
                                b'060112',
                                b'060112 Structural Biology (incl. Macromolecular Modelling)',
                            ),
                            (b'060113', b'060113 Synthetic Biology'),
                            (b'060114', b'060114 Systems Biology'),
                            (
                                b'060199',
                                b'060199 Biochemistry and Cell Biology not elsewhere classified',
                            ),
                            (b'0602', b'0602 ECOLOGY'),
                            (b'060201', b'060201 Behavioural Ecology'),
                            (
                                b'060202',
                                b'060202 Community Ecology (excl. Invasive Species Ecology)',
                            ),
                            (b'060203', b'060203 Ecological Physiology'),
                            (b'060204', b'060204 Freshwater Ecology'),
                            (
                                b'060205',
                                b'060205 Marine and Estuarine Ecology (incl. Marine Ichthyology)',
                            ),
                            (b'060206', b'060206 Palaeoecology'),
                            (b'060207', b'060207 Population Ecology'),
                            (b'060208', b'060208 Terrestrial Ecology'),
                            (
                                b'060299',
                                b'060299 Ecology not elsewhere classified',
                            ),
                            (b'0603', b'0603 EVOLUTIONARY BIOLOGY'),
                            (
                                b'060301',
                                b'060301 Animal Systematics and Taxonomy',
                            ),
                            (
                                b'060302',
                                b'060302 Biogeography and Phylogeography',
                            ),
                            (b'060303', b'060303 Biological Adaptation'),
                            (b'060304', b'060304 Ethology and Sociobiology'),
                            (
                                b'060305',
                                b'060305 Evolution of Developmental Systems',
                            ),
                            (
                                b'060306',
                                b'060306 Evolutionary Impacts of Climate Change',
                            ),
                            (b'060307', b'060307 Host-Parasite Interactions'),
                            (b'060308', b'060308 Life Histories'),
                            (
                                b'060309',
                                b'060309 Phylogeny and Comparative Analysis',
                            ),
                            (
                                b'060310',
                                b'060310 Plant Systematics and Taxonomy',
                            ),
                            (b'060311', b'060311 Speciation and Extinction'),
                            (
                                b'060399',
                                b'060399 Evolutionary Biology not elsewhere classified',
                            ),
                            (b'0604', b'0604 GENETICS'),
                            (b'060401', b'060401 Anthropological Genetics'),
                            (b'060402', b'060402 Cell and Nuclear Division'),
                            (
                                b'060403',
                                b'060403 Developmental Genetics (incl. Sex Determination)',
                            ),
                            (
                                b'060404',
                                b'060404 Epigenetics (incl. Genome Methylation and Epigenomics)',
                            ),
                            (
                                b'060405',
                                b'060405 Gene Expression (incl. Microarray and other genome-wide approaches)',
                            ),
                            (b'060406', b'060406 Genetic Immunology'),
                            (
                                b'060407',
                                b'060407 Genome Structure and Regulation',
                            ),
                            (b'060408', b'060408 Genomics'),
                            (b'060409', b'060409 Molecular Evolution'),
                            (b'060410', b'060410 Neurogenetics'),
                            (
                                b'060411',
                                b'060411 Population, Ecological and Evolutionary Genetics',
                            ),
                            (
                                b'060412',
                                b'060412 Quantitative Genetics (incl. Disease and Trait Mapping Genetics)',
                            ),
                            (
                                b'060499',
                                b'060499 Genetics not elsewhere classified',
                            ),
                            (b'0605', b'0605 MICROBIOLOGY'),
                            (b'060501', b'060501 Bacteriology'),
                            (b'060502', b'060502 Infectious Agents'),
                            (b'060503', b'060503 Microbial Genetics'),
                            (b'060504', b'060504 Microbial Ecology'),
                            (b'060505', b'060505 Mycology'),
                            (b'060506', b'060506 Virology'),
                            (
                                b'060599',
                                b'060599 Microbiology not elsewhere classified',
                            ),
                            (b'0606', b'0606 PHYSIOLOGY'),
                            (
                                b'060601',
                                b'060601 Animal Physiology - Biophysics',
                            ),
                            (b'060602', b'060602 Animal Physiology - Cell'),
                            (b'060603', b'060603 Animal Physiology - Systems'),
                            (b'060604', b'060604 Comparative Physiology'),
                            (
                                b'060699',
                                b'060699 Physiology not elsewhere classified',
                            ),
                            (b'0607', b'0607 PLANT BIOLOGY'),
                            (
                                b'060701',
                                b'060701 Phycology (incl. Marine Grasses)',
                            ),
                            (
                                b'060702',
                                b'060702 Plant Cell and Molecular Biology',
                            ),
                            (
                                b'060703',
                                b'060703 Plant Developmental and Reproductive Biology',
                            ),
                            (b'060704', b'060704 Plant Pathology'),
                            (b'060705', b'060705 Plant Physiology'),
                            (
                                b'060799',
                                b'060799 Plant Biology not elsewhere classified',
                            ),
                            (b'0608', b'0608 ZOOLOGY'),
                            (b'060801', b'060801 Animal Behaviour'),
                            (
                                b'060802',
                                b'060802 Animal Cell and Molecular Biology',
                            ),
                            (
                                b'060803',
                                b'060803 Animal Developmental and Reproductive Biology',
                            ),
                            (b'060804', b'060804 Animal Immunology'),
                            (b'060805', b'060805 Animal Neurobiology'),
                            (
                                b'060806',
                                b'060806 Animal Physiological Ecology',
                            ),
                            (
                                b'060807',
                                b'060807 Animal Structure and Function',
                            ),
                            (b'060808', b'060808 Invertebrate Biology'),
                            (b'060809', b'060809 Vertebrate Biology'),
                            (
                                b'060899',
                                b'060899 Zoology not elsewhere classified',
                            ),
                            (b'0699', b'0699 OTHER BIOLOGICAL SCIENCES'),
                            (b'069901', b'069901 Forensic Biology'),
                            (b'069902', b'069902 Global Change Biology'),
                            (
                                b'069999',
                                b'069999 Biological Sciences not elsewhere classified',
                            ),
                            (
                                b'07',
                                b'07 AGRICULTURAL AND VETERINARY SCIENCES',
                            ),
                            (
                                b'0701',
                                b'0701 AGRICULTURE, LAND AND FARM MANAGEMENT',
                            ),
                            (
                                b'070101',
                                b'070101 Agricultural Land Management',
                            ),
                            (b'070102', b'070102 Agricultural Land Planning'),
                            (
                                b'070103',
                                b'070103 Agricultural Production Systems Simulation',
                            ),
                            (
                                b'070104',
                                b'070104 Agricultural Spatial Analysis and Modelling',
                            ),
                            (
                                b'070105',
                                b'070105 Agricultural Systems Analysis and Modelling',
                            ),
                            (
                                b'070106',
                                b'070106 Farm Management, Rural Management and Agribusiness',
                            ),
                            (b'070107', b'070107 Farming Systems Research'),
                            (
                                b'070108',
                                b'070108 Sustainable Agricultural Development',
                            ),
                            (
                                b'070199',
                                b'070199 Agriculture, Land and Farm Management not elsewhere classified',
                            ),
                            (b'0702', b'0702 ANIMAL PRODUCTION'),
                            (b'070201', b'070201 Animal Breeding'),
                            (
                                b'070202',
                                b'070202 Animal Growth and Development',
                            ),
                            (b'070203', b'070203 Animal Management'),
                            (b'070204', b'070204 Animal Nutrition'),
                            (
                                b'070205',
                                b'070205 Animal Protection (Pests and Pathogens)',
                            ),
                            (b'070206', b'070206 Animal Reproduction'),
                            (b'070207', b'070207 Humane Animal Treatment'),
                            (
                                b'070299',
                                b'070299 Animal Production not elsewhere classified',
                            ),
                            (b'0703', b'0703 CROP AND PASTURE PRODUCTION'),
                            (
                                b'070301',
                                b'070301 Agro-ecosystem Function and Prediction',
                            ),
                            (b'070302', b'070302 Agronomy'),
                            (
                                b'070303',
                                b'070303 Crop and Pasture Biochemistry and Physiology',
                            ),
                            (
                                b'070304',
                                b'070304 Crop and Pasture Biomass and Bioproducts',
                            ),
                            (
                                b'070305',
                                b'070305 Crop and Pasture Improvement (Selection and Breeding)',
                            ),
                            (b'070306', b'070306 Crop and Pasture Nutrition'),
                            (
                                b'070307',
                                b'070307 Crop and Pasture Post Harvest Technologies (incl. Transportation and Storage)',
                            ),
                            (
                                b'070308',
                                b'070308 Crop and Pasture Protection (Pests, Diseases and Weeds)',
                            ),
                            (
                                b'070399',
                                b'070399 Crop and Pasture Production not elsewhere classified',
                            ),
                            (b'0704', b'0704 FISHERIES SCIENCES'),
                            (b'070401', b'070401 Aquaculture'),
                            (
                                b'070402',
                                b'070402 Aquatic Ecosystem Studies and Stock Assessment',
                            ),
                            (b'070403', b'070403 Fisheries Management'),
                            (b'070404', b'070404 Fish Pests and Diseases'),
                            (
                                b'070405',
                                b'070405 Fish Physiology and Genetics',
                            ),
                            (
                                b'070406',
                                b'070406 Post-Harvest Fisheries Technologies (incl. Transportation)',
                            ),
                            (
                                b'070499',
                                b'070499 Fisheries Sciences not elsewhere classified',
                            ),
                            (b'0705', b'0705 FORESTRY SCIENCES'),
                            (b'070501', b'070501 Agroforestry'),
                            (
                                b'070502',
                                b'070502 Forestry Biomass and Bioproducts',
                            ),
                            (b'070503', b'070503 Forestry Fire Management'),
                            (
                                b'070504',
                                b'070504 Forestry Management and Environment',
                            ),
                            (
                                b'070505',
                                b'070505 Forestry Pests, Health and Diseases',
                            ),
                            (
                                b'070506',
                                b'070506 Forestry Product Quality Assessment',
                            ),
                            (
                                b'070507',
                                b'070507 Tree Improvement (Selection and Breeding)',
                            ),
                            (
                                b'070508',
                                b'070508 Tree Nutrition and Physiology',
                            ),
                            (b'070509', b'070509 Wood Fibre Processing'),
                            (b'070510', b'070510 Wood Processing'),
                            (
                                b'070599',
                                b'070599 Forestry Sciences not elsewhere classified',
                            ),
                            (b'0706', b'0706 HORTICULTURAL PRODUCTION'),
                            (
                                b'070601',
                                b'070601 Horticultural Crop Growth and Development',
                            ),
                            (
                                b'070602',
                                b'070602 Horticultural Crop Improvement (Selection and Breeding)',
                            ),
                            (
                                b'070603',
                                b'070603 Horticultural Crop Protection (Pests, Diseases and Weeds)',
                            ),
                            (b'070604', b'070604 Oenology and Viticulture'),
                            (
                                b'070605',
                                b'070605 Post Harvest Horticultural Technologies (incl. Transportation and Storage)',
                            ),
                            (
                                b'070699',
                                b'070699 Horticultural Production not elsewhere classified',
                            ),
                            (b'0707', b'0707 VETERINARY SCIENCES'),
                            (
                                b'070701',
                                b'070701 Veterinary Anaesthesiology and Intensive Care',
                            ),
                            (
                                b'070702',
                                b'070702 Veterinary Anatomy and Physiology',
                            ),
                            (
                                b'070703',
                                b'070703 Veterinary Diagnosis and Diagnostics',
                            ),
                            (b'070704', b'070704 Veterinary Epidemiology'),
                            (b'070705', b'070705 Veterinary Immunology'),
                            (b'070706', b'070706 Veterinary Medicine'),
                            (
                                b'070707',
                                b'070707 Veterinary Microbiology (excl. Virology)',
                            ),
                            (b'070708', b'070708 Veterinary Parasitology'),
                            (b'070709', b'070709 Veterinary Pathology'),
                            (b'070710', b'070710 Veterinary Pharmacology'),
                            (b'070711', b'070711 Veterinary Surgery'),
                            (b'070712', b'070712 Veterinary Virology'),
                            (
                                b'070799',
                                b'070799 Veterinary Sciences not elsewhere classified',
                            ),
                            (
                                b'0799',
                                b'0799 OTHER AGRICULTURAL AND VETERINARY SCIENCES',
                            ),
                            (
                                b'079901',
                                b'079901 Agricultural Hydrology (Drainage, Flooding, Irrigation, Quality, etc.)',
                            ),
                            (
                                b'079902',
                                b'079902 Fertilisers and Agrochemicals (incl. Application)',
                            ),
                            (
                                b'079999',
                                b'079999 Agricultural and Veterinary Sciences not elsewhere classified',
                            ),
                            (b'08', b'08 INFORMATION AND COMPUTING SCIENCES'),
                            (
                                b'0801',
                                b'0801 ARTIFICIAL INTELLIGENCE AND IMAGE PROCESSING',
                            ),
                            (
                                b'080101',
                                b'080101 Adaptive Agents and Intelligent Robotics',
                            ),
                            (b'080102', b'080102 Artificial Life'),
                            (b'080103', b'080103 Computer Graphics'),
                            (b'080104', b'080104 Computer Vision'),
                            (b'080105', b'080105 Expert Systems'),
                            (b'080106', b'080106 Image Processing'),
                            (b'080107', b'080107 Natural Language Processing'),
                            (
                                b'080108',
                                b'080108 Neural, Evolutionary and Fuzzy Computation',
                            ),
                            (
                                b'080109',
                                b'080109 Pattern Recognition and Data Mining',
                            ),
                            (b'080110', b'080110 Simulation and Modelling'),
                            (
                                b'080111',
                                b'080111 Virtual Reality and Related Simulation',
                            ),
                            (
                                b'080199',
                                b'080199 Artificial Intelligence and Image Processing not elsewhere classified',
                            ),
                            (
                                b'0802',
                                b'0802 COMPUTATION THEORY AND MATHEMATICS',
                            ),
                            (
                                b'080201',
                                b'080201 Analysis of Algorithms and Complexity',
                            ),
                            (
                                b'080202',
                                b'080202 Applied Discrete Mathematics',
                            ),
                            (
                                b'080203',
                                b'080203 Computational Logic and Formal Languages',
                            ),
                            (b'080204', b'080204 Mathematical Software'),
                            (b'080205', b'080205 Numerical Computation'),
                            (
                                b'080299',
                                b'080299 Computation Theory and Mathematics not elsewhere classified',
                            ),
                            (b'0803', b'0803 COMPUTER SOFTWARE'),
                            (b'080301', b'080301 Bioinformatics Software'),
                            (
                                b'080302',
                                b'080302 Computer System Architecture',
                            ),
                            (b'080303', b'080303 Computer System Security'),
                            (b'080304', b'080304 Concurrent Programming'),
                            (b'080305', b'080305 Multimedia Programming'),
                            (b'080306', b'080306 Open Software'),
                            (b'080307', b'080307 Operating Systems'),
                            (b'080308', b'080308 Programming Languages'),
                            (b'080309', b'080309 Software Engineering'),
                            (
                                b'080399',
                                b'080399 Computer Software not elsewhere classified',
                            ),
                            (b'0804', b'0804 DATA FORMAT'),
                            (
                                b'080401',
                                b'080401 Coding and Information Theory',
                            ),
                            (b'080402', b'080402 Data Encryption'),
                            (b'080403', b'080403 Data Structures'),
                            (b'080404', b'080404 Markup Languages'),
                            (
                                b'080499',
                                b'080499 Data Format not elsewhere classified',
                            ),
                            (b'0805', b'0805 DISTRIBUTED COMPUTING'),
                            (
                                b'080501',
                                b'080501 Distributed and Grid Systems',
                            ),
                            (b'080502', b'080502 Mobile Technologies'),
                            (
                                b'080503',
                                b'080503 Networking and Communications',
                            ),
                            (b'080504', b'080504 Ubiquitous Computing'),
                            (
                                b'080505',
                                b'080505 Web Technologies (excl. Web Search)',
                            ),
                            (
                                b'080599',
                                b'080599 Distributed Computing not elsewhere classified',
                            ),
                            (b'0806', b'0806 INFORMATION SYSTEMS'),
                            (
                                b'080601',
                                b'080601 Aboriginal and Torres Strait Islander Information and Knowledge Systems',
                            ),
                            (b'080602', b'080602 Computer-Human Interaction'),
                            (b'080603', b'080603 Conceptual Modelling'),
                            (b'080604', b'080604 Database Management'),
                            (
                                b'080605',
                                b'080605 Decision Support and Group Support Systems',
                            ),
                            (b'080606', b'080606 Global Information Systems'),
                            (
                                b'080607',
                                b'080607 Information Engineering and Theory',
                            ),
                            (
                                b'080608',
                                b'080608 Information Systems Development Methodologies',
                            ),
                            (
                                b'080609',
                                b'080609 Information Systems Management',
                            ),
                            (
                                b'080610',
                                b'080610 Information Systems Organisation',
                            ),
                            (b'080611', b'080611 Information Systems Theory'),
                            (
                                b'080612',
                                b'080612 Interorganisational Information Systems and Web Services',
                            ),
                            (
                                b'080613',
                                b'080613 Maori Information and Knowledge Systems',
                            ),
                            (
                                b'080614',
                                b'080614 Pacific Peoples Information and Knowledge Systems',
                            ),
                            (
                                b'080699',
                                b'080699 Information Systems not elsewhere classified',
                            ),
                            (b'0807', b'0807 LIBRARY AND INFORMATION STUDIES'),
                            (
                                b'080701',
                                b'080701 Aboriginal and Torres Strait Islander Knowledge Management',
                            ),
                            (b'080702', b'080702 Health Informatics'),
                            (b'080703', b'080703 Human Information Behaviour'),
                            (
                                b'080704',
                                b'080704 Information Retrieval and Web Search',
                            ),
                            (b'080705', b'080705 Informetrics'),
                            (b'080706', b'080706 Librarianship'),
                            (
                                b'080707',
                                b'080707 Organisation of Information and Knowledge Resources',
                            ),
                            (
                                b'080708',
                                b'080708 Records and Information Management (excl. Business Records and Information Management)',
                            ),
                            (
                                b'080709',
                                b'080709 Social and Community Informatics',
                            ),
                            (
                                b'080799',
                                b'080799 Library and Information Studies not elsewhere classified',
                            ),
                            (
                                b'0899',
                                b'0899 OTHER INFORMATION AND COMPUTING SCIENCES',
                            ),
                            (
                                b'089999',
                                b'089999 Information and Computing Sciences not elsewhere classified',
                            ),
                            (b'09', b'09 ENGINEERING'),
                            (b'0901', b'0901 AEROSPACE ENGINEERING'),
                            (
                                b'090101',
                                b'090101 Aerodynamics (excl. Hypersonic Aerodynamics)',
                            ),
                            (b'090102', b'090102 Aerospace Materials'),
                            (b'090103', b'090103 Aerospace Structures'),
                            (
                                b'090104',
                                b'090104 Aircraft Performance and Flight Control Systems',
                            ),
                            (b'090105', b'090105 Avionics'),
                            (b'090106', b'090106 Flight Dynamics'),
                            (
                                b'090107',
                                b'090107 Hypersonic Propulsion and Hypersonic Aerodynamics',
                            ),
                            (
                                b'090108',
                                b'090108 Satellite, Space Vehicle and Missile Design and Testing',
                            ),
                            (
                                b'090199',
                                b'090199 Aerospace Engineering not elsewhere classified',
                            ),
                            (b'0902', b'0902 AUTOMOTIVE ENGINEERING'),
                            (
                                b'090201',
                                b'090201 Automotive Combustion and Fuel Engineering (incl. Alternative/Renewable Fuels)',
                            ),
                            (
                                b'090202',
                                b'090202 Automotive Engineering Materials',
                            ),
                            (b'090203', b'090203 Automotive Mechatronics'),
                            (
                                b'090204',
                                b'090204 Automotive Safety Engineering',
                            ),
                            (
                                b'090205',
                                b'090205 Hybrid Vehicles and Powertrains',
                            ),
                            (
                                b'090299',
                                b'090299 Automotive Engineering not elsewhere classified',
                            ),
                            (b'0903', b'0903 BIOMEDICAL ENGINEERING'),
                            (b'090301', b'090301 Biomaterials'),
                            (b'090302', b'090302 Biomechanical Engineering'),
                            (b'090303', b'090303 Biomedical Instrumentation'),
                            (b'090304', b'090304 Medical Devices'),
                            (b'090305', b'090305 Rehabilitation Engineering'),
                            (
                                b'090399',
                                b'090399 Biomedical Engineering not elsewhere classified',
                            ),
                            (b'0904', b'0904 CHEMICAL ENGINEERING'),
                            (
                                b'090401',
                                b'090401 Carbon Capture Engineering (excl. Sequestration)',
                            ),
                            (
                                b'090402',
                                b'090402 Catalytic Process Engineering',
                            ),
                            (b'090403', b'090403 Chemical Engineering Design'),
                            (
                                b'090404',
                                b'090404 Membrane and Separation Technologies',
                            ),
                            (
                                b'090405',
                                b'090405 Non-automotive Combustion and Fuel Engineering (incl. Alternative/Renewable Fuels)',
                            ),
                            (
                                b'090406',
                                b'090406 Powder and Particle Technology',
                            ),
                            (
                                b'090407',
                                b'090407 Process Control and Simulation',
                            ),
                            (b'090408', b'090408 Rheology'),
                            (
                                b'090409',
                                b'090409 Wastewater Treatment Processes',
                            ),
                            (b'090410', b'090410 Water Treatment Processes'),
                            (
                                b'090499',
                                b'090499 Chemical Engineering not elsewhere classified',
                            ),
                            (b'0905', b'0905 CIVIL ENGINEERING'),
                            (
                                b'090501',
                                b'090501 Civil Geotechnical Engineering',
                            ),
                            (b'090502', b'090502 Construction Engineering'),
                            (b'090503', b'090503 Construction Materials'),
                            (b'090504', b'090504 Earthquake Engineering'),
                            (
                                b'090505',
                                b'090505 Infrastructure Engineering and Asset Management',
                            ),
                            (b'090506', b'090506 Structural Engineering'),
                            (b'090507', b'090507 Transport Engineering'),
                            (b'090508', b'090508 Water Quality Engineering'),
                            (b'090509', b'090509 Water Resources Engineering'),
                            (
                                b'090599',
                                b'090599 Civil Engineering not elsewhere classified',
                            ),
                            (
                                b'0906',
                                b'0906 ELECTRICAL AND ELECTRONIC ENGINEERING',
                            ),
                            (b'090601', b'090601 Circuits and Systems'),
                            (
                                b'090602',
                                b'090602 Control Systems, Robotics and Automation',
                            ),
                            (b'090603', b'090603 Industrial Electronics'),
                            (
                                b'090604',
                                b'090604 Microelectronics and Integrated Circuits',
                            ),
                            (
                                b'090605',
                                b'090605 Photodetectors, Optical Sensors and Solar Cells',
                            ),
                            (
                                b'090606',
                                b'090606 Photonics and Electro-Optical Engineering (excl. Communications)',
                            ),
                            (
                                b'090607',
                                b'090607 Power and Energy Systems Engineering (excl. Renewable Power)',
                            ),
                            (
                                b'090608',
                                b'090608 Renewable Power and Energy Systems Engineering (excl. Solar Cells)',
                            ),
                            (b'090609', b'090609 Signal Processing'),
                            (
                                b'090699',
                                b'090699 Electrical and Electronic Engineering not elsewhere classified',
                            ),
                            (b'0907', b'0907 ENVIRONMENTAL ENGINEERING'),
                            (
                                b'090701',
                                b'090701 Environmental Engineering Design',
                            ),
                            (
                                b'090702',
                                b'090702 Environmental Engineering Modelling',
                            ),
                            (b'090703', b'090703 Environmental Technologies'),
                            (
                                b'090799',
                                b'090799 Environmental Engineering not elsewhere classified',
                            ),
                            (b'0908', b'0908 FOOD SCIENCES'),
                            (
                                b'090801',
                                b'090801 Food Chemistry and Molecular Gastronomy (excl. Wine)',
                            ),
                            (b'090802', b'090802 Food Engineering'),
                            (b'090803', b'090803 Food Nutritional Balance'),
                            (
                                b'090804',
                                b'090804 Food Packaging, Preservation and Safety',
                            ),
                            (b'090805', b'090805 Food Processing'),
                            (
                                b'090806',
                                b'090806 Wine Chemistry and Wine Sensory Science',
                            ),
                            (
                                b'090899',
                                b'090899 Food Sciences not elsewhere classified',
                            ),
                            (b'0909', b'0909 GEOMATIC ENGINEERING'),
                            (b'090901', b'090901 Cartography'),
                            (b'090902', b'090902 Geodesy'),
                            (
                                b'090903',
                                b'090903 Geospatial Information Systems',
                            ),
                            (
                                b'090904',
                                b'090904 Navigation and Position Fixing',
                            ),
                            (
                                b'090905',
                                b'090905 Photogrammetry and Remote Sensing',
                            ),
                            (
                                b'090906',
                                b'090906 Surveying (incl. Hydrographic Surveying)',
                            ),
                            (
                                b'090999',
                                b'090999 Geomatic Engineering not elsewhere classified',
                            ),
                            (b'0910', b'0910 MANUFACTURING ENGINEERING'),
                            (b'091001', b'091001 CAD/CAM Systems'),
                            (
                                b'091002',
                                b'091002 Flexible Manufacturing Systems',
                            ),
                            (b'091003', b'091003 Machine Tools'),
                            (b'091004', b'091004 Machining'),
                            (b'091005', b'091005 Manufacturing Management'),
                            (
                                b'091006',
                                b'091006 Manufacturing Processes and Technologies (excl. Textiles)',
                            ),
                            (
                                b'091007',
                                b'091007 Manufacturing Robotics and Mechatronics (excl. Automotive Mechatronics)',
                            ),
                            (
                                b'091008',
                                b'091008 Manufacturing Safety and Quality',
                            ),
                            (b'091009', b'091009 Microtechnology'),
                            (
                                b'091010',
                                b'091010 Packaging, Storage and Transportation (excl. Food and Agricultural Products)',
                            ),
                            (b'091011', b'091011 Precision Engineering'),
                            (b'091012', b'091012 Textile Technology'),
                            (
                                b'091099',
                                b'091099 Manufacturing Engineering not elsewhere classified',
                            ),
                            (b'0911', b'0911 MARITIME ENGINEERING'),
                            (b'091101', b'091101 Marine Engineering'),
                            (b'091102', b'091102 Naval Architecture'),
                            (b'091103', b'091103 Ocean Engineering'),
                            (
                                b'091104',
                                b'091104 Ship and Platform Hydrodynamics',
                            ),
                            (
                                b'091105',
                                b'091105 Ship and Platform Structures',
                            ),
                            (b'091106', b'091106 Special Vehicles'),
                            (
                                b'091199',
                                b'091199 Maritime Engineering not elsewhere classified',
                            ),
                            (b'0912', b'0912 MATERIALS ENGINEERING'),
                            (b'091201', b'091201 Ceramics'),
                            (
                                b'091202',
                                b'091202 Composite and Hybrid Materials',
                            ),
                            (b'091203', b'091203 Compound Semiconductors'),
                            (b'091204', b'091204 Elemental Semiconductors'),
                            (b'091205', b'091205 Functional Materials'),
                            (b'091206', b'091206 Glass'),
                            (b'091207', b'091207 Metals and Alloy Materials'),
                            (b'091208', b'091208 Organic Semiconductors'),
                            (b'091209', b'091209 Polymers and Plastics'),
                            (b'091210', b'091210 Timber, Pulp and Paper'),
                            (
                                b'091299',
                                b'091299 Materials Engineering not elsewhere classified',
                            ),
                            (b'0913', b'0913 MECHANICAL ENGINEERING'),
                            (
                                b'091301',
                                b'091301 Acoustics and Noise Control (excl. Architectural Acoustics)',
                            ),
                            (
                                b'091302',
                                b'091302 Automation and Control Engineering',
                            ),
                            (b'091303', b'091303 Autonomous Vehicles'),
                            (
                                b'091304',
                                b'091304 Dynamics, Vibration and Vibration Control',
                            ),
                            (
                                b'091305',
                                b'091305 Energy Generation, Conversion and Storage Engineering',
                            ),
                            (
                                b'091306',
                                b'091306 Microelectromechanical Systems (MEMS)',
                            ),
                            (
                                b'091307',
                                b'091307 Numerical Modelling and Mechanical Characterisation',
                            ),
                            (b'091308', b'091308 Solid Mechanics'),
                            (b'091309', b'091309 Tribology'),
                            (
                                b'091399',
                                b'091399 Mechanical Engineering not elsewhere classified',
                            ),
                            (
                                b'0914',
                                b'0914 RESOURCES ENGINEERING AND EXTRACTIVE METALLURGY',
                            ),
                            (b'091401', b'091401 Electrometallurgy'),
                            (
                                b'091402',
                                b'091402 Geomechanics and Resources Geotechnical Engineering',
                            ),
                            (b'091403', b'091403 Hydrometallurgy'),
                            (
                                b'091404',
                                b'091404 Mineral Processing/Beneficiation',
                            ),
                            (b'091405', b'091405 Mining Engineering'),
                            (
                                b'091406',
                                b'091406 Petroleum and Reservoir Engineering',
                            ),
                            (b'091407', b'091407 Pyrometallurgy'),
                            (
                                b'091499',
                                b'091499 Resources Engineering and Extractive Metallurgy not elsewhere classified',
                            ),
                            (b'0915', b'0915 INTERDISCIPLINARY ENGINEERING'),
                            (
                                b'091501',
                                b'091501 Computational Fluid Dynamics',
                            ),
                            (b'091502', b'091502 Computational Heat Transfer'),
                            (b'091503', b'091503 Engineering Practice'),
                            (
                                b'091504',
                                b'091504 Fluidisation and Fluid Mechanics',
                            ),
                            (
                                b'091505',
                                b'091505 Heat and Mass Transfer Operations',
                            ),
                            (
                                b'091506',
                                b'091506 Nuclear Engineering (incl. Fuel Enrichment and Waste Processing and Storage)',
                            ),
                            (
                                b'091507',
                                b'091507 Risk Engineering (excl. Earthquake Engineering)',
                            ),
                            (b'091508', b'091508 Turbulent Flows'),
                            (
                                b'091599',
                                b'091599 Interdisciplinary Engineering not elsewhere classified',
                            ),
                            (b'0999', b'0999 OTHER ENGINEERING'),
                            (b'099901', b'099901 Agricultural Engineering'),
                            (b'099902', b'099902 Engineering Instrumentation'),
                            (
                                b'099999',
                                b'099999 Engineering not elsewhere classified',
                            ),
                            (b'10', b'10 TECHNOLOGY'),
                            (b'1001', b'1001 AGRICULTURAL BIOTECHNOLOGY'),
                            (
                                b'100101',
                                b'100101 Agricultural Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100102',
                                b'100102 Agricultural Marine Biotechnology',
                            ),
                            (
                                b'100103',
                                b'100103 Agricultural Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100104',
                                b'100104 Genetically Modified Animals',
                            ),
                            (
                                b'100105',
                                b'100105 Genetically Modified Field Crops and Pasture',
                            ),
                            (
                                b'100106',
                                b'100106 Genetically Modified Horticulture Plants',
                            ),
                            (b'100107', b'100107 Genetically Modified Trees'),
                            (b'100108', b'100108 Livestock Cloning'),
                            (b'100109', b'100109 Transgenesis'),
                            (
                                b'100199',
                                b'100199 Agricultural Biotechnology not elsewhere classified',
                            ),
                            (b'1002', b'1002 ENVIRONMENTAL BIOTECHNOLOGY'),
                            (b'100201', b'100201 Biodiscovery'),
                            (b'100202', b'100202 Biological Control'),
                            (b'100203', b'100203 Bioremediation'),
                            (
                                b'100204',
                                b'100204 Environmental Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100205',
                                b'100205 Environmental Marine Biotechnology',
                            ),
                            (
                                b'100206',
                                b'100206 Environmental Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100299',
                                b'100299 Environmental Biotechnology not elsewhere classified',
                            ),
                            (b'1003', b'1003 INDUSTRIAL BIOTECHNOLOGY'),
                            (
                                b'100301',
                                b'100301 Biocatalysis and Enzyme Technology',
                            ),
                            (
                                b'100302',
                                b'100302 Bioprocessing, Bioproduction and Bioproducts',
                            ),
                            (b'100303', b'100303 Fermentation'),
                            (
                                b'100304',
                                b'100304 Industrial Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100305',
                                b'100305 Industrial Microbiology (incl. Biofeedstocks)',
                            ),
                            (
                                b'100306',
                                b'100306 Industrial Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100399',
                                b'100399 Industrial Biotechnology not elsewhere classified',
                            ),
                            (b'1004', b'1004 MEDICAL BIOTECHNOLOGY'),
                            (b'100401', b'100401 Gene and Molecular Therapy'),
                            (
                                b'100402',
                                b'100402 Medical Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100403',
                                b'100403 Medical Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100404',
                                b'100404 Regenerative Medicine (incl. Stem Cells and Tissue Engineering)',
                            ),
                            (
                                b'100499',
                                b'100499 Medical Biotechnology not elsewhere classified',
                            ),
                            (b'1005', b'1005 COMMUNICATIONS TECHNOLOGIES'),
                            (b'100501', b'100501 Antennas and Propagation'),
                            (
                                b'100502',
                                b'100502 Broadband and Modem Technology',
                            ),
                            (
                                b'100503',
                                b'100503 Computer Communications Networks',
                            ),
                            (b'100504', b'100504 Data Communications'),
                            (
                                b'100505',
                                b'100505 Microwave and Millimetrewave Theory and Technology',
                            ),
                            (
                                b'100506',
                                b'100506 Optical Fibre Communications',
                            ),
                            (
                                b'100507',
                                b'100507 Optical Networks and Systems',
                            ),
                            (b'100508', b'100508 Satellite Communications'),
                            (b'100509', b'100509 Video Communications'),
                            (b'100510', b'100510 Wireless Communications'),
                            (
                                b'100599',
                                b'100599 Communications Technologies not elsewhere classified',
                            ),
                            (b'1006', b'1006 COMPUTER HARDWARE'),
                            (
                                b'100601',
                                b'100601 Arithmetic and Logic Structures',
                            ),
                            (
                                b'100602',
                                b'100602 Input, Output and Data Devices',
                            ),
                            (b'100603', b'100603 Logic Design'),
                            (b'100604', b'100604 Memory Structures'),
                            (
                                b'100605',
                                b'100605 Performance Evaluation; Testing and Simulation of Reliability',
                            ),
                            (b'100606', b'100606 Processor Architectures'),
                            (
                                b'100699',
                                b'100699 Computer Hardware not elsewhere classified',
                            ),
                            (b'1007', b'1007 NANOTECHNOLOGY'),
                            (
                                b'100701',
                                b'100701 Environmental Nanotechnology',
                            ),
                            (
                                b'100702',
                                b'100702 Molecular and Organic Electronics',
                            ),
                            (b'100703', b'100703 Nanobiotechnology'),
                            (
                                b'100704',
                                b'100704 Nanoelectromechanical Systems',
                            ),
                            (b'100705', b'100705 Nanoelectronics'),
                            (
                                b'100706',
                                b'100706 Nanofabrication, Growth and Self Assembly',
                            ),
                            (b'100707', b'100707 Nanomanufacturing'),
                            (b'100708', b'100708 Nanomaterials'),
                            (b'100709', b'100709 Nanomedicine'),
                            (b'100710', b'100710 Nanometrology'),
                            (b'100711', b'100711 Nanophotonics'),
                            (b'100712', b'100712 Nanoscale Characterisation'),
                            (
                                b'100713',
                                b'100713 Nanotoxicology, Health and Safety',
                            ),
                            (
                                b'100799',
                                b'100799 Nanotechnology not elsewhere classified',
                            ),
                            (b'1099', b'1099 OTHER TECHNOLOGY'),
                            (
                                b'109999',
                                b'109999 Technology not elsewhere classified',
                            ),
                            (b'11', b'11 MEDICAL AND HEALTH SCIENCES'),
                            (
                                b'1101',
                                b'1101 MEDICAL BIOCHEMISTRY AND METABOLOMICS',
                            ),
                            (
                                b'110101',
                                b'110101 Medical Biochemistry: Amino Acids and Metabolites',
                            ),
                            (
                                b'110102',
                                b'110102 Medical Biochemistry: Carbohydrates',
                            ),
                            (
                                b'110103',
                                b'110103 Medical Biochemistry: Inorganic Elements and Compounds',
                            ),
                            (
                                b'110104',
                                b'110104 Medical Biochemistry: Lipids',
                            ),
                            (
                                b'110105',
                                b'110105 Medical Biochemistry: Nucleic Acids',
                            ),
                            (
                                b'110106',
                                b'110106 Medical Biochemistry: Proteins and Peptides (incl. Medical Proteomics)',
                            ),
                            (b'110107', b'110107 Metabolic Medicine'),
                            (
                                b'110199',
                                b'110199 Medical Biochemistry and Metabolomics not elsewhere classified',
                            ),
                            (
                                b'1102',
                                b'1102 CARDIORESPIRATORY MEDICINE AND HAEMATOLOGY',
                            ),
                            (
                                b'110201',
                                b'110201 Cardiology (incl. Cardiovascular Diseases)',
                            ),
                            (b'110202', b'110202 Haematology'),
                            (b'110203', b'110203 Respiratory Diseases'),
                            (
                                b'110299',
                                b'110299 Cardiorespiratory Medicine and Haematology not elsewhere classified',
                            ),
                            (b'1103', b'1103 CLINICAL SCIENCES'),
                            (b'110301', b'110301 Anaesthesiology'),
                            (
                                b'110302',
                                b'110302 Clinical Chemistry (diagnostics)',
                            ),
                            (b'110303', b'110303 Clinical Microbiology'),
                            (b'110304', b'110304 Dermatology'),
                            (b'110305', b'110305 Emergency Medicine'),
                            (b'110306', b'110306 Endocrinology'),
                            (
                                b'110307',
                                b'110307 Gastroenterology and Hepatology',
                            ),
                            (b'110308', b'110308 Geriatrics and Gerontology'),
                            (b'110309', b'110309 Infectious Diseases'),
                            (b'110310', b'110310 Intensive Care'),
                            (
                                b'110311',
                                b'110311 Medical Genetics (excl. Cancer Genetics)',
                            ),
                            (b'110312', b'110312 Nephrology and Urology'),
                            (b'110313', b'110313 Nuclear Medicine'),
                            (b'110314', b'110314 Orthopaedics'),
                            (b'110315', b'110315 Otorhinolaryngology'),
                            (
                                b'110316',
                                b'110316 Pathology (excl. Oral Pathology)',
                            ),
                            (b'110317', b'110317 Physiotherapy'),
                            (b'110318', b'110318 Podiatry'),
                            (
                                b'110319',
                                b'110319 Psychiatry (incl. Psychotherapy)',
                            ),
                            (b'110320', b'110320 Radiology and Organ Imaging'),
                            (
                                b'110321',
                                b'110321 Rehabilitation and Therapy (excl. Physiotherapy)',
                            ),
                            (b'110322', b'110322 Rheumatology and Arthritis'),
                            (b'110323', b'110323 Surgery'),
                            (b'110324', b'110324 Venereology'),
                            (
                                b'110399',
                                b'110399 Clinical Sciences not elsewhere classified',
                            ),
                            (
                                b'1104',
                                b'1104 COMPLEMENTARY AND ALTERNATIVE MEDICINE',
                            ),
                            (b'110401', b'110401 Chiropractic'),
                            (b'110402', b'110402 Naturopathy'),
                            (
                                b'110403',
                                b'110403 Traditional Aboriginal and Torres Strait Islander Medicine and Treatments',
                            ),
                            (
                                b'110404',
                                b'110404 Traditional Chinese Medicine and Treatments',
                            ),
                            (
                                b'110405',
                                b'110405 Traditional Maori Medicine and Treatments',
                            ),
                            (
                                b'110499',
                                b'110499 Complementary and Alternative Medicine not elsewhere classified',
                            ),
                            (b'1105', b'1105 DENTISTRY'),
                            (
                                b'110501',
                                b'110501 Dental Materials and Equipment',
                            ),
                            (
                                b'110502',
                                b'110502 Dental Therapeutics, Pharmacology and Toxicology',
                            ),
                            (b'110503', b'110503 Endodontics'),
                            (
                                b'110504',
                                b'110504 Oral and Maxillofacial Surgery',
                            ),
                            (b'110505', b'110505 Oral Medicine and Pathology'),
                            (
                                b'110506',
                                b'110506 Orthodontics and Dentofacial Orthopaedics',
                            ),
                            (b'110507', b'110507 Paedodontics'),
                            (b'110508', b'110508 Periodontics'),
                            (b'110509', b'110509 Special Needs Dentistry'),
                            (
                                b'110599',
                                b'110599 Dentistry not elsewhere classified',
                            ),
                            (
                                b'1106',
                                b'1106 HUMAN MOVEMENT AND SPORTS SCIENCE',
                            ),
                            (b'110601', b'110601 Biomechanics'),
                            (b'110602', b'110602 Exercise Physiology'),
                            (b'110603', b'110603 Motor Control'),
                            (b'110604', b'110604 Sports Medicine'),
                            (
                                b'110699',
                                b'110699 Human Movement and Sports Science not elsewhere classified',
                            ),
                            (b'1107', b'1107 IMMUNOLOGY'),
                            (b'110701', b'110701 Allergy'),
                            (
                                b'110702',
                                b'110702 Applied Immunology (incl. Antibody Engineering, Xenotransplantation and T-cell Therapies)',
                            ),
                            (b'110703', b'110703 Autoimmunity'),
                            (b'110704', b'110704 Cellular Immunology'),
                            (
                                b'110705',
                                b'110705 Humoural Immunology and Immunochemistry',
                            ),
                            (
                                b'110706',
                                b'110706 Immunogenetics (incl. Genetic Immunology)',
                            ),
                            (b'110707', b'110707 Innate Immunity'),
                            (b'110708', b'110708 Transplantation Immunology'),
                            (b'110709', b'110709 Tumour Immunology'),
                            (
                                b'110799',
                                b'110799 Immunology not elsewhere classified',
                            ),
                            (b'1108', b'1108 MEDICAL MICROBIOLOGY'),
                            (b'110801', b'110801 Medical Bacteriology'),
                            (
                                b'110802',
                                b'110802 Medical Infection Agents (incl. Prions)',
                            ),
                            (b'110803', b'110803 Medical Parasitology'),
                            (b'110804', b'110804 Medical Virology'),
                            (
                                b'110899',
                                b'110899 Medical Microbiology not elsewhere classified',
                            ),
                            (b'1109', b'1109 NEUROSCIENCES'),
                            (b'110901', b'110901 Autonomic Nervous System'),
                            (b'110902', b'110902 Cellular Nervous System'),
                            (b'110903', b'110903 Central Nervous System'),
                            (
                                b'110904',
                                b'110904 Neurology and Neuromuscular Diseases',
                            ),
                            (b'110905', b'110905 Peripheral Nervous System'),
                            (b'110906', b'110906 Sensory Systems'),
                            (
                                b'110999',
                                b'110999 Neurosciences not elsewhere classified',
                            ),
                            (b'1110', b'1110 NURSING'),
                            (b'111001', b'111001 Aged Care Nursing'),
                            (
                                b'111002',
                                b'111002 Clinical Nursing: Primary (Preventative)',
                            ),
                            (
                                b'111003',
                                b'111003 Clinical Nursing: Secondary (Acute Care)',
                            ),
                            (
                                b'111004',
                                b'111004 Clinical Nursing: Tertiary (Rehabilitative)',
                            ),
                            (b'111005', b'111005 Mental Health Nursing'),
                            (b'111006', b'111006 Midwifery'),
                            (
                                b'111099',
                                b'111099 Nursing not elsewhere classified',
                            ),
                            (b'1111', b'1111 NUTRITION AND DIETETICS'),
                            (
                                b'111101',
                                b'111101 Clinical and Sports Nutrition',
                            ),
                            (b'111102', b'111102 Dietetics and Nutrigenomics'),
                            (b'111103', b'111103 Nutritional Physiology'),
                            (
                                b'111104',
                                b'111104 Public Nutrition Intervention',
                            ),
                            (
                                b'111199',
                                b'111199 Nutrition and Dietetics not elsewhere classified',
                            ),
                            (b'1112', b'1112 ONCOLOGY AND CARCINOGENESIS'),
                            (b'111201', b'111201 Cancer Cell Biology'),
                            (b'111202', b'111202 Cancer Diagnosis'),
                            (b'111203', b'111203 Cancer Genetics'),
                            (
                                b'111204',
                                b'111204 Cancer Therapy (excl. Chemotherapy and Radiation Therapy)',
                            ),
                            (b'111205', b'111205 Chemotherapy'),
                            (b'111206', b'111206 Haematological Tumours'),
                            (b'111207', b'111207 Molecular Targets'),
                            (b'111208', b'111208 Radiation Therapy'),
                            (b'111209', b'111209 Solid Tumours'),
                            (
                                b'111299',
                                b'111299 Oncology and Carcinogenesis not elsewhere classified',
                            ),
                            (b'1113', b'1113 OPHTHALMOLOGY AND OPTOMETRY'),
                            (b'111301', b'111301 Ophthalmology'),
                            (b'111302', b'111302 Optical Technology'),
                            (b'111303', b'111303 Vision Science'),
                            (
                                b'111399',
                                b'111399 Ophthalmology and Optometry not elsewhere classified',
                            ),
                            (
                                b'1114',
                                b'1114 PAEDIATRICS AND REPRODUCTIVE MEDICINE',
                            ),
                            (
                                b'111401',
                                b'111401 Foetal Development and Medicine',
                            ),
                            (b'111402', b'111402 Obstetrics and Gynaecology'),
                            (b'111403', b'111403 Paediatrics'),
                            (b'111404', b'111404 Reproduction'),
                            (
                                b'111499',
                                b'111499 Paediatrics and Reproductive Medicine not elsewhere classified',
                            ),
                            (
                                b'1115',
                                b'1115 PHARMACOLOGY AND PHARMACEUTICAL SCIENCES',
                            ),
                            (b'111501', b'111501 Basic Pharmacology'),
                            (
                                b'111502',
                                b'111502 Clinical Pharmacology and Therapeutics',
                            ),
                            (
                                b'111503',
                                b'111503 Clinical Pharmacy and Pharmacy Practice',
                            ),
                            (b'111504', b'111504 Pharmaceutical Sciences'),
                            (b'111505', b'111505 Pharmacogenomics'),
                            (
                                b'111506',
                                b'111506 Toxicology (incl. Clinical Toxicology)',
                            ),
                            (
                                b'111599',
                                b'111599 Pharmacology and Pharmaceutical Sciences not elsewhere classified',
                            ),
                            (b'1116', b'1116 MEDICAL PHYSIOLOGY'),
                            (b'111601', b'111601 Cell Physiology'),
                            (b'111602', b'111602 Human Biophysics'),
                            (b'111603', b'111603 Systems Physiology'),
                            (
                                b'111699',
                                b'111699 Medical Physiology not elsewhere classified',
                            ),
                            (
                                b'1117',
                                b'1117 PUBLIC HEALTH AND HEALTH SERVICES',
                            ),
                            (
                                b'111701',
                                b'111701 Aboriginal and Torres Strait Islander Health',
                            ),
                            (b'111702', b'111702 Aged Health Care'),
                            (b'111703', b'111703 Care for Disabled'),
                            (b'111704', b'111704 Community Child Health'),
                            (
                                b'111705',
                                b'111705 Environmental and Occupational Health and Safety',
                            ),
                            (b'111706', b'111706 Epidemiology'),
                            (b'111707', b'111707 Family Care'),
                            (
                                b'111708',
                                b'111708 Health and Community Services',
                            ),
                            (b'111709', b'111709 Health Care Administration'),
                            (b'111710', b'111710 Health Counselling'),
                            (
                                b'111711',
                                b'111711 Health Information Systems (incl. Surveillance)',
                            ),
                            (b'111712', b'111712 Health Promotion'),
                            (b'111713', b'111713 Maori Health'),
                            (b'111714', b'111714 Mental Health'),
                            (b'111715', b'111715 Pacific Peoples Health'),
                            (b'111716', b'111716 Preventive Medicine'),
                            (b'111717', b'111717 Primary Health Care'),
                            (b'111718', b'111718 Residential Client Care'),
                            (
                                b'111799',
                                b'111799 Public Health and Health Services not elsewhere classified',
                            ),
                            (
                                b'1199',
                                b'1199 OTHER MEDICAL AND HEALTH SCIENCES',
                            ),
                            (
                                b'119999',
                                b'119999 Medical and Health Sciences not elsewhere classified',
                            ),
                            (b'12', b'12 BUILT ENVIRONMENT AND DESIGN'),
                            (b'1201', b'1201 ARCHITECTURE'),
                            (b'120101', b'120101 Architectural Design'),
                            (
                                b'120102',
                                b'120102 Architectural Heritage and Conservation',
                            ),
                            (
                                b'120103',
                                b'120103 Architectural History and Theory',
                            ),
                            (
                                b'120104',
                                b'120104 Architectural Science and Technology (incl. Acoustics, Lighting, Structure and Ecologically Sustainable Design)',
                            ),
                            (b'120105', b'120105 Architecture Management'),
                            (b'120106', b'120106 Interior Design'),
                            (b'120107', b'120107 Landscape Architecture'),
                            (
                                b'120199',
                                b'120199 Architecture not elsewhere classified',
                            ),
                            (b'1202', b'1202 BUILDING'),
                            (
                                b'120201',
                                b'120201 Building Construction Management and Project Planning',
                            ),
                            (
                                b'120202',
                                b'120202 Building Science and Techniques',
                            ),
                            (b'120203', b'120203 Quantity Surveying'),
                            (
                                b'120299',
                                b'120299 Building not elsewhere classified',
                            ),
                            (b'1203', b'1203 DESIGN PRACTICE AND MANAGEMENT'),
                            (b'120301', b'120301 Design History and Theory'),
                            (b'120302', b'120302 Design Innovation'),
                            (
                                b'120303',
                                b'120303 Design Management and Studio and Professional Practice',
                            ),
                            (
                                b'120304',
                                b'120304 Digital and Interaction Design',
                            ),
                            (b'120305', b'120305 Industrial Design'),
                            (b'120306', b'120306 Textile and Fashion Design'),
                            (
                                b'120307',
                                b'120307 Visual Communication Design (incl. Graphic Design)',
                            ),
                            (
                                b'120399',
                                b'120399 Design Practice and Management not elsewhere classified',
                            ),
                            (b'1204', b'1204 ENGINEERING DESIGN'),
                            (
                                b'120401',
                                b'120401 Engineering Design Empirical Studies',
                            ),
                            (
                                b'120402',
                                b'120402 Engineering Design Knowledge',
                            ),
                            (b'120403', b'120403 Engineering Design Methods'),
                            (b'120404', b'120404 Engineering Systems Design'),
                            (
                                b'120405',
                                b'120405 Models of Engineering Design',
                            ),
                            (
                                b'120499',
                                b'120499 Engineering Design not elsewhere classified',
                            ),
                            (b'1205', b'1205 URBAN AND REGIONAL PLANNING'),
                            (b'120501', b'120501 Community Planning'),
                            (
                                b'120502',
                                b'120502 History and Theory of the Built Environment (excl. Architecture)',
                            ),
                            (
                                b'120503',
                                b'120503 Housing Markets, Development, Management',
                            ),
                            (
                                b'120504',
                                b'120504 Land Use and Environmental Planning',
                            ),
                            (
                                b'120505',
                                b'120505 Regional Analysis and Development',
                            ),
                            (b'120506', b'120506 Transport Planning'),
                            (
                                b'120507',
                                b'120507 Urban Analysis and Development',
                            ),
                            (b'120508', b'120508 Urban Design'),
                            (
                                b'120599',
                                b'120599 Urban and Regional Planning not elsewhere classified',
                            ),
                            (
                                b'1299',
                                b'1299 OTHER BUILT ENVIRONMENT AND DESIGN',
                            ),
                            (
                                b'129999',
                                b'129999 Built Environment and Design not elsewhere classified',
                            ),
                            (b'13', b'13 EDUCATION'),
                            (b'1301', b'1301 EDUCATION SYSTEMS'),
                            (
                                b'130101',
                                b'130101 Continuing and Community Education',
                            ),
                            (
                                b'130102',
                                b'130102 Early Childhood Education (excl. Maori)',
                            ),
                            (b'130103', b'130103 Higher Education'),
                            (
                                b'130104',
                                b'130104 Kura Kaupapa Maori (Maori Primary Education)',
                            ),
                            (
                                b'130105',
                                b'130105 Primary Education (excl. Maori)',
                            ),
                            (b'130106', b'130106 Secondary Education'),
                            (
                                b'130107',
                                b'130107 Te Whariki (Maori Early Childhood Education)',
                            ),
                            (
                                b'130108',
                                b'130108 Technical, Further and Workplace Education',
                            ),
                            (
                                b'130199',
                                b'130199 Education systems not elsewhere classified',
                            ),
                            (b'1302', b'1302 CURRICULUM AND PEDAGOGY'),
                            (
                                b'130201',
                                b'130201 Creative Arts, Media and Communication Curriculum and Pedagogy',
                            ),
                            (
                                b'130202',
                                b'130202 Curriculum and Pedagogy Theory and Development',
                            ),
                            (
                                b'130203',
                                b'130203 Economics, Business and Management Curriculum and Pedagogy',
                            ),
                            (
                                b'130204',
                                b'130204 English and Literacy Curriculum and Pedagogy (excl. LOTE, ESL and TESOL)',
                            ),
                            (
                                b'130205',
                                b'130205 Humanities and Social Sciences Curriculum and Pedagogy (excl. Economics, Business and Management)',
                            ),
                            (
                                b'130206',
                                b'130206 Kohanga Reo (Maori Language Curriculum and Pedagogy)',
                            ),
                            (
                                b'130207',
                                b'130207 LOTE, ESL and TESOL Curriculum and Pedagogy (excl. Maori)',
                            ),
                            (
                                b'130208',
                                b'130208 Mathematics and Numeracy Curriculum and Pedagogy',
                            ),
                            (
                                b'130209',
                                b'130209 Medicine, Nursing and Health Curriculum and Pedagogy',
                            ),
                            (
                                b'130210',
                                b'130210 Physical Education and Development Curriculum and Pedagogy',
                            ),
                            (
                                b'130211',
                                b'130211 Religion Curriculum and Pedagogy',
                            ),
                            (
                                b'130212',
                                b'130212 Science, Technology and Engineering Curriculum and Pedagogy',
                            ),
                            (
                                b'130213',
                                b'130213 Vocational Education and Training Curriculum and Pedagogy',
                            ),
                            (
                                b'130299',
                                b'130299 Curriculum and Pedagogy not elsewhere classified',
                            ),
                            (b'1303', b'1303 SPECIALIST STUDIES IN EDUCATION'),
                            (
                                b'130301',
                                b'130301 Aboriginal and Torres Strait Islander Education',
                            ),
                            (
                                b'130302',
                                b'130302 Comparative and Cross-Cultural Education',
                            ),
                            (
                                b'130303',
                                b'130303 Education Assessment and Evaluation',
                            ),
                            (
                                b'130304',
                                b'130304 Educational Administration, Management and Leadership',
                            ),
                            (b'130305', b'130305 Educational Counselling'),
                            (
                                b'130306',
                                b'130306 Educational Technology and Computing',
                            ),
                            (
                                b'130307',
                                b'130307 Ethnic Education (excl. Aboriginal and Torres Strait Islander, Maori and Pacific Peoples)',
                            ),
                            (
                                b'130308',
                                b'130308 Gender, Sexuality and Education',
                            ),
                            (b'130309', b'130309 Learning Sciences'),
                            (
                                b'130310',
                                b'130310 Maori Education (excl. Early Childhood and Primary Education)',
                            ),
                            (b'130311', b'130311 Pacific Peoples Education'),
                            (
                                b'130312',
                                b'130312 Special Education and Disability',
                            ),
                            (
                                b'130313',
                                b'130313 Teacher Education and Professional Development of Educators',
                            ),
                            (
                                b'130399',
                                b'130399 Specialist Studies in Education not elsewhere classified',
                            ),
                            (b'1399', b'1399 OTHER EDUCATION'),
                            (
                                b'139999',
                                b'139999 Education not elsewhere classified',
                            ),
                            (b'14', b'14 ECONOMICS'),
                            (b'1401', b'1401 ECONOMIC THEORY'),
                            (b'140101', b'140101 History of Economic Thought'),
                            (b'140102', b'140102 Macroeconomic Theory'),
                            (b'140103', b'140103 Mathematical Economics'),
                            (b'140104', b'140104 Microeconomic Theory'),
                            (
                                b'140199',
                                b'140199 Economic Theory not elsewhere classified',
                            ),
                            (b'1402', b'1402 APPLIED ECONOMICS'),
                            (b'140201', b'140201 Agricultural Economics'),
                            (
                                b'140202',
                                b'140202 Economic Development and Growth',
                            ),
                            (b'140203', b'140203 Economic History'),
                            (b'140204', b'140204 Economics of Education'),
                            (
                                b'140205',
                                b'140205 Environment and Resource Economics',
                            ),
                            (b'140206', b'140206 Experimental Economics'),
                            (b'140207', b'140207 Financial Economics'),
                            (b'140208', b'140208 Health Economics'),
                            (
                                b'140209',
                                b'140209 Industry Economics and Industrial Organisation',
                            ),
                            (
                                b'140210',
                                b'140210 International Economics and International Finance',
                            ),
                            (b'140211', b'140211 Labour Economics'),
                            (
                                b'140212',
                                b'140212 Macroeconomics (incl. Monetary and Fiscal Theory)',
                            ),
                            (
                                b'140213',
                                b'140213 Public Economics- Public Choice',
                            ),
                            (
                                b'140214',
                                b'140214 Public Economics- Publically Provided Goods',
                            ),
                            (
                                b'140215',
                                b'140215 Public Economics- Taxation and Revenue',
                            ),
                            (b'140216', b'140216 Tourism Economics'),
                            (b'140217', b'140217 Transport Economics'),
                            (
                                b'140218',
                                b'140218 Urban and Regional Economics',
                            ),
                            (b'140219', b'140219 Welfare Economics'),
                            (
                                b'140299',
                                b'140299 Applied Economics not elsewhere classified',
                            ),
                            (b'1403', b'1403 ECONOMETRICS'),
                            (b'140301', b'140301 Cross-Sectional Analysis'),
                            (
                                b'140302',
                                b'140302 Econometric and Statistical Methods',
                            ),
                            (
                                b'140303',
                                b'140303 Economic Models and Forecasting',
                            ),
                            (b'140304', b'140304 Panel Data Analysis'),
                            (b'140305', b'140305 Time-Series Analysis'),
                            (
                                b'140399',
                                b'140399 Econometrics not elsewhere classified',
                            ),
                            (b'1499', b'1499 OTHER ECONOMICS'),
                            (
                                b'149901',
                                b'149901 Comparative Economic Systems',
                            ),
                            (b'149902', b'149902 Ecological Economics'),
                            (b'149903', b'149903 Heterodox Economics'),
                            (
                                b'149999',
                                b'149999 Economics not elsewhere classified',
                            ),
                            (
                                b'15',
                                b'15 COMMERCE, MANAGEMENT, TOURISM AND SERVICES',
                            ),
                            (
                                b'1501',
                                b'1501 ACCOUNTING, AUDITING AND ACCOUNTABILITY',
                            ),
                            (
                                b'150101',
                                b'150101 Accounting Theory and Standards',
                            ),
                            (b'150102', b'150102 Auditing and Accountability'),
                            (b'150103', b'150103 Financial Accounting'),
                            (b'150104', b'150104 International Accounting'),
                            (b'150105', b'150105 Management Accounting'),
                            (
                                b'150106',
                                b'150106 Sustainability Accounting and Reporting',
                            ),
                            (b'150107', b'150107 Taxation Accounting'),
                            (
                                b'150199',
                                b'150199 Accounting, Auditing and Accountability not elsewhere classified',
                            ),
                            (b'1502', b'1502 BANKING, FINANCE AND INVESTMENT'),
                            (b'150201', b'150201 Finance'),
                            (b'150202', b'150202 Financial Econometrics'),
                            (
                                b'150203',
                                b'150203 Financial Institutions (incl. Banking)',
                            ),
                            (b'150204', b'150204 Insurance Studies'),
                            (
                                b'150205',
                                b'150205 Investment and Risk Management',
                            ),
                            (
                                b'150299',
                                b'150299 Banking, Finance and Investment not elsewhere classified',
                            ),
                            (b'1503', b'1503 BUSINESS AND MANAGEMENT'),
                            (
                                b'150301',
                                b'150301 Business Information Management (incl. Records, Knowledge and Information Management, and Intelligence)',
                            ),
                            (
                                b'150302',
                                b'150302 Business Information Systems',
                            ),
                            (
                                b'150303',
                                b'150303 Corporate Governance and Stakeholder Engagement',
                            ),
                            (b'150304', b'150304 Entrepreneurship'),
                            (b'150305', b'150305 Human Resources Management'),
                            (b'150306', b'150306 Industrial Relations'),
                            (
                                b'150307',
                                b'150307 Innovation and Technology Management',
                            ),
                            (b'150308', b'150308 International Business'),
                            (
                                b'150309',
                                b'150309 Logistics and Supply Chain Management',
                            ),
                            (
                                b'150310',
                                b'150310 Organisation and Management Theory',
                            ),
                            (b'150311', b'150311 Organisational Behaviour'),
                            (
                                b'150312',
                                b'150312 Organisational Planning and Management',
                            ),
                            (b'150313', b'150313 Quality Management'),
                            (b'150314', b'150314 Small Business Management'),
                            (
                                b'150399',
                                b'150399 Business and Management not elsewhere classified',
                            ),
                            (b'1504', b'1504 COMMERCIAL SERVICES'),
                            (
                                b'150401',
                                b'150401 Food and Hospitality Services',
                            ),
                            (b'150402', b'150402 Hospitality Management'),
                            (
                                b'150403',
                                b'150403 Real Estate and Valuation Services',
                            ),
                            (
                                b'150404',
                                b'150404 Sport and Leisure Management',
                            ),
                            (
                                b'150499',
                                b'150499 Commercial Services not elsewhere classified',
                            ),
                            (b'1505', b'1505 MARKETING'),
                            (
                                b'150501',
                                b'150501 Consumer-Oriented Product or Service Development',
                            ),
                            (b'150502', b'150502 Marketing Communications'),
                            (
                                b'150503',
                                b'150503 Marketing Management (incl. Strategy and Customer Relations)',
                            ),
                            (b'150504', b'150504 Marketing Measurement'),
                            (
                                b'150505',
                                b'150505 Marketing Research Methodology',
                            ),
                            (b'150506', b'150506 Marketing Theory'),
                            (
                                b'150507',
                                b'150507 Pricing (incl. Consumer Value Estimation)',
                            ),
                            (
                                b'150599',
                                b'150599 Marketing not elsewhere classified',
                            ),
                            (b'1506', b'1506 TOURISM'),
                            (b'150601', b'150601 Impacts of Tourism'),
                            (b'150602', b'150602 Tourism Forecasting'),
                            (b'150603', b'150603 Tourism Management'),
                            (b'150604', b'150604 Tourism Marketing'),
                            (b'150605', b'150605 Tourism Resource Appraisal'),
                            (
                                b'150606',
                                b'150606 Tourist Behaviour and Visitor Experience',
                            ),
                            (
                                b'150699',
                                b'150699 Tourism not elsewhere classified',
                            ),
                            (
                                b'1507',
                                b'1507 TRANSPORTATION AND FREIGHT SERVICES',
                            ),
                            (
                                b'150701',
                                b'150701 Air Transportation and Freight Services',
                            ),
                            (
                                b'150702',
                                b'150702 Rail Transportation and Freight Services',
                            ),
                            (
                                b'150703',
                                b'150703 Road Transportation and Freight Services',
                            ),
                            (
                                b'150799',
                                b'150799 Transportation and Freight Services not elsewhere classified',
                            ),
                            (
                                b'1599',
                                b'1599 OTHER COMMERCE, MANAGEMENT, TOURISM AND SERVICES',
                            ),
                            (
                                b'159999',
                                b'159999 Commerce, Management, Tourism and Services not elsewhere classified',
                            ),
                            (b'16', b'16 STUDIES IN HUMAN SOCIETY'),
                            (b'1601', b'1601 ANTHROPOLOGY'),
                            (b'160101', b'160101 Anthropology of Development'),
                            (
                                b'160102',
                                b'160102 Biological (Physical) Anthropology',
                            ),
                            (b'160103', b'160103 Linguistic Anthropology'),
                            (
                                b'160104',
                                b'160104 Social and Cultural Anthropology',
                            ),
                            (
                                b'160199',
                                b'160199 Anthropology not elsewhere classified',
                            ),
                            (b'1602', b'1602 CRIMINOLOGY'),
                            (
                                b'160201',
                                b'160201 Causes and Prevention of Crime',
                            ),
                            (
                                b'160202',
                                b'160202 Correctional Theory, Offender Treatment and Rehabilitation',
                            ),
                            (b'160203', b'160203 Courts and Sentencing'),
                            (b'160204', b'160204 Criminological Theories'),
                            (
                                b'160205',
                                b'160205 Police Administration, Procedures and Practice',
                            ),
                            (
                                b'160206',
                                b'160206 Private Policing and Security Services',
                            ),
                            (
                                b'160299',
                                b'160299 Criminology not elsewhere classified',
                            ),
                            (b'1603', b'1603 DEMOGRAPHY'),
                            (
                                b'160301',
                                b'160301 Family and Household Studies',
                            ),
                            (b'160302', b'160302 Fertility'),
                            (b'160303', b'160303 Migration'),
                            (b'160304', b'160304 Mortality'),
                            (
                                b'160305',
                                b'160305 Population Trends and Policies',
                            ),
                            (
                                b'160399',
                                b'160399 Demography not elsewhere classified',
                            ),
                            (b'1604', b'1604 HUMAN GEOGRAPHY'),
                            (b'160401', b'160401 Economic Geography'),
                            (
                                b'160402',
                                b'160402 Recreation, Leisure and Tourism Geography',
                            ),
                            (
                                b'160403',
                                b'160403 Social and Cultural Geography',
                            ),
                            (
                                b'160404',
                                b'160404 Urban and Regional Studies (excl. Planning)',
                            ),
                            (
                                b'160499',
                                b'160499 Human Geography not elsewhere classified',
                            ),
                            (b'1605', b'1605 POLICY AND ADMINISTRATION'),
                            (
                                b'160501',
                                b'160501 Aboriginal and Torres Strait Islander Policy',
                            ),
                            (b'160502', b'160502 Arts and Cultural Policy'),
                            (
                                b'160503',
                                b'160503 Communications and Media Policy',
                            ),
                            (b'160504', b'160504 Crime Policy'),
                            (b'160505', b'160505 Economic Development Policy'),
                            (b'160506', b'160506 Education Policy'),
                            (b'160507', b'160507 Environment Policy'),
                            (b'160508', b'160508 Health Policy'),
                            (b'160509', b'160509 Public Administration'),
                            (b'160510', b'160510 Public Policy'),
                            (
                                b'160511',
                                b'160511 Research, Science and Technology Policy',
                            ),
                            (b'160512', b'160512 Social Policy'),
                            (b'160513', b'160513 Tourism Policy'),
                            (b'160514', b'160514 Urban Policy'),
                            (
                                b'160599',
                                b'160599 Policy and Administration not elsewhere classified',
                            ),
                            (b'1606', b'1606 POLITICAL SCIENCE'),
                            (
                                b'160601',
                                b'160601 Australian Government and Politics',
                            ),
                            (b'160602', b'160602 Citizenship'),
                            (
                                b'160603',
                                b'160603 Comparative Government and Politics',
                            ),
                            (b'160604', b'160604 Defence Studies'),
                            (b'160605', b'160605 Environmental Politics'),
                            (
                                b'160606',
                                b'160606 Government and Politics of Asia and the Pacific',
                            ),
                            (b'160607', b'160607 International Relations'),
                            (
                                b'160608',
                                b'160608 New Zealand Government and Politics',
                            ),
                            (
                                b'160609',
                                b'160609 Political Theory and Political Philosophy',
                            ),
                            (
                                b'160699',
                                b'160699 Political Science not elsewhere classified',
                            ),
                            (b'1607', b'1607 SOCIAL WORK'),
                            (
                                b'160701',
                                b'160701 Clinical Social Work Practice',
                            ),
                            (
                                b'160702',
                                b'160702 Counselling, Welfare and Community Services',
                            ),
                            (b'160703', b'160703 Social Program Evaluation'),
                            (
                                b'160799',
                                b'160799 Social Work not elsewhere classified',
                            ),
                            (b'1608', b'1608 SOCIOLOGY'),
                            (
                                b'160801',
                                b'160801 Applied Sociology, Program Evaluation and Social Impact Assessment',
                            ),
                            (b'160802', b'160802 Environmental Sociology'),
                            (b'160803', b'160803 Race and Ethnic Relations'),
                            (b'160804', b'160804 Rural Sociology'),
                            (b'160805', b'160805 Social Change'),
                            (b'160806', b'160806 Social Theory'),
                            (
                                b'160807',
                                b'160807 Sociological Methodology and Research Methods',
                            ),
                            (
                                b'160808',
                                b'160808 Sociology and Social Studies of Science and Technology',
                            ),
                            (b'160809', b'160809 Sociology of Education'),
                            (
                                b'160810',
                                b'160810 Urban Sociology and Community Studies',
                            ),
                            (
                                b'160899',
                                b'160899 Sociology not elsewhere classified',
                            ),
                            (b'1699', b'1699 OTHER STUDIES IN HUMAN SOCIETY'),
                            (b'169901', b'169901 Gender Specific Studies'),
                            (
                                b'169902',
                                b'169902 Studies of Aboriginal and Torres Strait Islander Society',
                            ),
                            (b'169903', b'169903 Studies of Asian Society'),
                            (b'169904', b'169904 Studies of Maori Society'),
                            (
                                b'169905',
                                b"169905 Studies of Pacific Peoples' Societies",
                            ),
                            (
                                b'169999',
                                b'169999 Studies in Human Society not elsewhere classified',
                            ),
                            (b'17', b'17 PSYCHOLOGY AND COGNITIVE SCIENCES'),
                            (b'1701', b'1701 PSYCHOLOGY'),
                            (
                                b'170101',
                                b'170101 Biological Psychology (Neuropsychology, Psychopharmacology, Physiological Psychology)',
                            ),
                            (
                                b'170102',
                                b'170102 Developmental Psychology and Ageing',
                            ),
                            (b'170103', b'170103 Educational Psychology'),
                            (b'170104', b'170104 Forensic Psychology'),
                            (b'170105', b'170105 Gender Psychology'),
                            (
                                b'170106',
                                b'170106 Health, Clinical and Counselling Psychology',
                            ),
                            (
                                b'170107',
                                b'170107 Industrial and Organisational Psychology',
                            ),
                            (b'170108', b'170108 Kaupapa Maori Psychology'),
                            (
                                b'170109',
                                b'170109 Personality, Abilities and Assessment',
                            ),
                            (
                                b'170110',
                                b'170110 Psychological Methodology, Design and Analysis',
                            ),
                            (b'170111', b'170111 Psychology of Religion'),
                            (
                                b'170112',
                                b'170112 Sensory Processes, Perception and Performance',
                            ),
                            (
                                b'170113',
                                b'170113 Social and Community Psychology',
                            ),
                            (
                                b'170114',
                                b'170114 Sport and Exercise Psychology',
                            ),
                            (
                                b'170199',
                                b'170199 Psychology not elsewhere classified',
                            ),
                            (b'1702', b'1702 COGNITIVE SCIENCES'),
                            (
                                b'170201',
                                b'170201 Computer Perception, Memory and Attention',
                            ),
                            (b'170202', b'170202 Decision Making'),
                            (
                                b'170203',
                                b'170203 Knowledge Representation and Machine Learning',
                            ),
                            (
                                b'170204',
                                b'170204 Linguistic Processes (incl. Speech Production and Comprehension)',
                            ),
                            (
                                b'170205',
                                b'170205 Neurocognitive Patterns and Neural Networks',
                            ),
                            (
                                b'170299',
                                b'170299 Cognitive Sciences not elsewhere classified',
                            ),
                            (
                                b'1799',
                                b'1799 OTHER PSYCHOLOGY AND COGNITIVE SCIENCES',
                            ),
                            (
                                b'179999',
                                b'179999 Psychology and Cognitive Sciences not elsewhere classified',
                            ),
                            (b'18', b'18 LAW AND LEGAL STUDIES'),
                            (b'1801', b'1801 LAW'),
                            (
                                b'180101',
                                b'180101 Aboriginal and Torres Strait Islander Law',
                            ),
                            (b'180102', b'180102 Access to Justice'),
                            (b'180103', b'180103 Administrative Law'),
                            (b'180104', b'180104 Civil Law and Procedure'),
                            (b'180105', b'180105 Commercial and Contract Law'),
                            (b'180106', b'180106 Comparative Law'),
                            (
                                b'180107',
                                b'180107 Conflict of Laws (Private International Law)',
                            ),
                            (b'180108', b'180108 Constitutional Law'),
                            (
                                b'180109',
                                b'180109 Corporations and Associations Law',
                            ),
                            (b'180110', b'180110 Criminal Law and Procedure'),
                            (
                                b'180111',
                                b'180111 Environmental and Natural Resources Law',
                            ),
                            (b'180112', b'180112 Equity and Trusts Law'),
                            (b'180113', b'180113 Family Law'),
                            (b'180114', b'180114 Human Rights Law'),
                            (b'180115', b'180115 Intellectual Property Law'),
                            (
                                b'180116',
                                b'180116 International Law (excl. International Trade Law)',
                            ),
                            (b'180117', b'180117 International Trade Law'),
                            (b'180118', b'180118 Labour Law'),
                            (b'180119', b'180119 Law and Society'),
                            (
                                b'180120',
                                b'180120 Legal Institutions (incl. Courts and Justice Systems)',
                            ),
                            (
                                b'180121',
                                b'180121 Legal Practice, Lawyering and the Legal Profession',
                            ),
                            (
                                b'180122',
                                b'180122 Legal Theory, Jurisprudence and Legal Interpretation',
                            ),
                            (
                                b'180123',
                                b'180123 Litigation, Adjudication and Dispute Resolution',
                            ),
                            (
                                b'180124',
                                b'180124 Property Law (excl. Intellectual Property Law)',
                            ),
                            (b'180125', b'180125 Taxation Law'),
                            (b'180126', b'180126 Tort Law'),
                            (
                                b'180199',
                                b'180199 Law not elsewhere classified',
                            ),
                            (b'1802', b'1802 MAORI LAW'),
                            (
                                b'180201',
                                b'180201 Nga Tikanga Maori (Maori Customary Law)',
                            ),
                            (
                                b'180202',
                                b'180202 Te Maori Whakahaere Rauemi (Maori Resource Law))',
                            ),
                            (
                                b'180203',
                                b'180203 Te Tiriti o Waitangi (The Treaty of Waitangi)',
                            ),
                            (
                                b'180204',
                                b'180204 Te Ture Whenua (Maori Land Law)',
                            ),
                            (
                                b'180299',
                                b'180299 Maori Law not elsewhere classified',
                            ),
                            (b'1899', b'1899 OTHER LAW AND LEGAL STUDIES'),
                            (
                                b'189999',
                                b'189999 Law and Legal Studies not elsewhere classified',
                            ),
                            (
                                b'19',
                                b'19 STUDIES IN CREATIVE ARTS AND WRITING',
                            ),
                            (b'1901', b'1901 ART THEORY AND CRITICISM'),
                            (b'190101', b'190101 Art Criticism'),
                            (b'190102', b'190102 Art History'),
                            (b'190103', b'190103 Art Theory'),
                            (b'190104', b'190104 Visual Cultures'),
                            (
                                b'190199',
                                b'190199 Art Theory and Criticism not elsewhere classified',
                            ),
                            (
                                b'1902',
                                b'1902 FILM, TELEVISION AND DIGITAL MEDIA',
                            ),
                            (b'190201', b'190201 Cinema Studies'),
                            (
                                b'190202',
                                b'190202 Computer Gaming and Animation',
                            ),
                            (b'190203', b'190203 Electronic Media Art'),
                            (b'190204', b'190204 Film and Television'),
                            (b'190205', b'190205 Interactive Media'),
                            (
                                b'190299',
                                b'190299 Film, Television and Digital Media not elsewhere classified',
                            ),
                            (
                                b'1903',
                                b'1903 JOURNALISM AND PROFESSIONAL WRITING',
                            ),
                            (b'190301', b'190301 Journalism Studies'),
                            (b'190302', b'190302 Professional Writing'),
                            (b'190303', b'190303 Technical Writing'),
                            (
                                b'190399',
                                b'190399 Journalism and Professional Writing not elsewhere classified',
                            ),
                            (
                                b'1904',
                                b'1904 PERFORMING ARTS AND CREATIVE WRITING',
                            ),
                            (
                                b'190401',
                                b'190401 Aboriginal and Torres Strait Islander Performing Arts',
                            ),
                            (
                                b'190402',
                                b'190402 Creative Writing (incl. Playwriting)',
                            ),
                            (b'190403', b'190403 Dance'),
                            (
                                b'190404',
                                b'190404 Drama, Theatre and Performance Studies',
                            ),
                            (b'190405', b'190405 Maori Performing Arts'),
                            (b'190406', b'190406 Music Composition'),
                            (b'190407', b'190407 Music Performance'),
                            (b'190408', b'190408 Music Therapy'),
                            (
                                b'190409',
                                b'190409 Musicology and Ethnomusicology',
                            ),
                            (
                                b'190410',
                                b'190410 Pacific Peoples Performing Arts',
                            ),
                            (
                                b'190499',
                                b'190499 Performing Arts and Creative Writing not elsewhere classified',
                            ),
                            (b'1905', b'1905 VISUAL ARTS AND CRAFTS'),
                            (b'190501', b'190501 Crafts'),
                            (
                                b'190502',
                                b'190502 Fine Arts (incl. Sculpture and Painting)',
                            ),
                            (b'190503', b'190503 Lens-based Practice'),
                            (
                                b'190504',
                                b'190504 Performance and Installation Art',
                            ),
                            (
                                b'190599',
                                b'190599 Visual Arts and Crafts not elsewhere classified',
                            ),
                            (
                                b'1999',
                                b'1999 OTHER STUDIES IN CREATIVE ARTS AND WRITING',
                            ),
                            (
                                b'199999',
                                b'199999 Studies in Creative Arts and Writing not elsewhere classified',
                            ),
                            (b'20', b'20 LANGUAGE, COMMUNICATION AND CULTURE'),
                            (b'2001', b'2001 COMMUNICATION AND MEDIA STUDIES'),
                            (b'200101', b'200101 Communication Studies'),
                            (
                                b'200102',
                                b'200102 Communication Technology and Digital Media Studies',
                            ),
                            (
                                b'200103',
                                b'200103 International and Development Communication',
                            ),
                            (b'200104', b'200104 Media Studies'),
                            (
                                b'200105',
                                b'200105 Organisational, Interpersonal and Intercultural Communication',
                            ),
                            (
                                b'200199',
                                b'200199 Communication and Media Studies not elsewhere classified',
                            ),
                            (b'2002', b'2002 CULTURAL STUDIES'),
                            (
                                b'200201',
                                b'200201 Aboriginal and Torres Strait Islander Cultural Studies',
                            ),
                            (b'200202', b'200202 Asian Cultural Studies'),
                            (
                                b'200203',
                                b'200203 Consumption and Everyday Life',
                            ),
                            (b'200204', b'200204 Cultural Theory'),
                            (b'200205', b'200205 Culture, Gender, Sexuality'),
                            (b'200206', b'200206 Globalisation and Culture'),
                            (b'200207', b'200207 Maori Cultural Studies'),
                            (b'200208', b'200208 Migrant Cultural Studies'),
                            (
                                b'200209',
                                b'200209 Multicultural, Intercultural and Cross-cultural Studies',
                            ),
                            (b'200210', b'200210 Pacific Cultural Studies'),
                            (b'200211', b'200211 Postcolonial Studies'),
                            (b'200212', b'200212 Screen and Media Culture'),
                            (
                                b'200299',
                                b'200299 Cultural Studies not elsewhere classified',
                            ),
                            (b'2003', b'2003 LANGUAGE STUDIES'),
                            (b'200301', b'200301 Early English Languages'),
                            (b'200302', b'200302 English Language'),
                            (
                                b'200303',
                                b'200303 English as a Second Language',
                            ),
                            (
                                b'200304',
                                b'200304 Central and Eastern European Languages (incl. Russian)',
                            ),
                            (
                                b'200305',
                                b'200305 Latin and Classical Greek Languages',
                            ),
                            (b'200306', b'200306 French Language'),
                            (b'200307', b'200307 German Language'),
                            (b'200308', b'200308 Iberian Languages'),
                            (b'200309', b'200309 Italian Language'),
                            (b'200310', b'200310 Other European Languages'),
                            (b'200311', b'200311 Chinese Languages'),
                            (b'200312', b'200312 Japanese Language'),
                            (b'200313', b'200313 Indonesian Languages'),
                            (
                                b'200314',
                                b'200314 South-East Asian Languages (excl. Indonesian)',
                            ),
                            (b'200315', b'200315 Indian Languages'),
                            (b'200316', b'200316 Korean Language'),
                            (
                                b'200317',
                                b'200317 Other Asian Languages (excl. South-East Asian)',
                            ),
                            (b'200318', b'200318 Middle Eastern Languages'),
                            (
                                b'200319',
                                b'200319 Aboriginal and Torres Strait Islander Languages',
                            ),
                            (b'200320', b'200320 Pacific Languages'),
                            (
                                b'200321',
                                b'200321 Te Reo Maori (Maori Language)',
                            ),
                            (
                                b'200322',
                                b'200322 Comparative Language Studies',
                            ),
                            (
                                b'200323',
                                b'200323 Translation and Interpretation Studies',
                            ),
                            (
                                b'200399',
                                b'200399 Language Studies not elsewhere classified',
                            ),
                            (b'2004', b'2004 LINGUISTICS'),
                            (
                                b'200401',
                                b'200401 Applied Linguistics and Educational Linguistics',
                            ),
                            (b'200402', b'200402 Computational Linguistics'),
                            (b'200403', b'200403 Discourse and Pragmatics'),
                            (
                                b'200404',
                                b'200404 Laboratory Phonetics and Speech Science',
                            ),
                            (
                                b'200405',
                                b'200405 Language in Culture and Society (Sociolinguistics)',
                            ),
                            (
                                b'200406',
                                b'200406 Language in Time and Space (incl. Historical Linguistics, Dialectology)',
                            ),
                            (b'200407', b'200407 Lexicography'),
                            (
                                b'200408',
                                b'200408 Linguistic Structures (incl. Grammar, Phonology, Lexicon, Semantics)',
                            ),
                            (
                                b'200499',
                                b'200499 Linguistics not elsewhere classified',
                            ),
                            (b'2005', b'2005 LITERARY STUDIES'),
                            (
                                b'200501',
                                b'200501 Aboriginal and Torres Strait Islander Literature',
                            ),
                            (
                                b'200502',
                                b'200502 Australian Literature (excl. Aboriginal and Torres Strait Islander Literature)',
                            ),
                            (
                                b'200503',
                                b'200503 British and Irish Literature',
                            ),
                            (b'200504', b'200504 Maori Literature'),
                            (
                                b'200505',
                                b'200505 New Zealand Literature (excl. Maori Literature)',
                            ),
                            (b'200506', b'200506 North American Literature'),
                            (b'200507', b'200507 Pacific Literature'),
                            (
                                b'200508',
                                b'200508 Other Literatures in English',
                            ),
                            (
                                b'200509',
                                b'200509 Central and Eastern European Literature (incl. Russian)',
                            ),
                            (
                                b'200510',
                                b'200510 Latin and Classical Greek Literature',
                            ),
                            (b'200511', b'200511 Literature in French'),
                            (b'200512', b'200512 Literature in German'),
                            (b'200513', b'200513 Literature in Italian'),
                            (
                                b'200514',
                                b'200514 Literature in Spanish and Portuguese',
                            ),
                            (b'200515', b'200515 Other European Literature'),
                            (b'200516', b'200516 Indonesian Literature'),
                            (b'200517', b'200517 Literature in Chinese'),
                            (b'200518', b'200518 Literature in Japanese'),
                            (
                                b'200519',
                                b'200519 South-East Asian Literature (excl. Indonesian)',
                            ),
                            (b'200520', b'200520 Indian Literature'),
                            (b'200521', b'200521 Korean Literature'),
                            (
                                b'200522',
                                b'200522 Other Asian Literature (excl. South-East Asian)',
                            ),
                            (b'200523', b'200523 Middle Eastern Literature'),
                            (
                                b'200524',
                                b'200524 Comparative Literature Studies',
                            ),
                            (b'200525', b'200525 Literary Theory'),
                            (
                                b'200526',
                                b'200526 Stylistics and Textual Analysis',
                            ),
                            (
                                b'200599',
                                b'200599 Literary Studies not elsewhere classified',
                            ),
                            (
                                b'2099',
                                b'2099 OTHER LANGUAGE, COMMUNICATION AND CULTURE',
                            ),
                            (
                                b'209999',
                                b'209999 Language, Communication and Culture not elsewhere classified',
                            ),
                            (b'21', b'21 HISTORY AND ARCHAEOLOGY'),
                            (b'2101', b'2101 ARCHAEOLOGY'),
                            (
                                b'210101',
                                b'210101 Aboriginal and Torres Strait Islander Archaeology',
                            ),
                            (b'210102', b'210102 Archaeological Science'),
                            (
                                b'210103',
                                b'210103 Archaeology of Asia, Africa and the Americas',
                            ),
                            (
                                b'210104',
                                b'210104 Archaeology of Australia (excl. Aboriginal and Torres Strait Islander)',
                            ),
                            (
                                b'210105',
                                b'210105 Archaeology of Europe, the Mediterranean and the Levant',
                            ),
                            (
                                b'210106',
                                b'210106 Archaeology of New Guinea and Pacific Islands (excl. New Zealand)',
                            ),
                            (
                                b'210107',
                                b'210107 Archaeology of New Zealand (excl. Maori)',
                            ),
                            (
                                b'210108',
                                b'210108 Historical Archaeology (incl. Industrial Archaeology)',
                            ),
                            (b'210109', b'210109 Maori Archaeology'),
                            (b'210110', b'210110 Maritime Archaeology'),
                            (
                                b'210199',
                                b'210199 Archaeology not elsewhere classified',
                            ),
                            (b'2102', b'2102 CURATORIAL AND RELATED STUDIES'),
                            (
                                b'210201',
                                b'210201 Archival, Repository and Related Studies',
                            ),
                            (
                                b'210202',
                                b'210202 Heritage and Cultural Conservation',
                            ),
                            (b'210203', b'210203 Materials Conservation'),
                            (b'210204', b'210204 Museum Studies'),
                            (
                                b'210299',
                                b'210299 Curatorial and Related Studies not elsewhere classified',
                            ),
                            (b'2103', b'2103 HISTORICAL STUDIES'),
                            (
                                b'210301',
                                b'210301 Aboriginal and Torres Strait Islander History',
                            ),
                            (b'210302', b'210302 Asian History'),
                            (
                                b'210303',
                                b'210303 Australian History (excl. Aboriginal and Torres Strait Islander History)',
                            ),
                            (b'210304', b'210304 Biography'),
                            (b'210305', b'210305 British History'),
                            (
                                b'210306',
                                b'210306 Classical Greek and Roman History',
                            ),
                            (
                                b'210307',
                                b'210307 European History (excl. British, Classical Greek and Roman)',
                            ),
                            (b'210308', b'210308 Latin American History'),
                            (b'210309', b'210309 Maori History'),
                            (
                                b'210310',
                                b'210310 Middle Eastern and African History',
                            ),
                            (b'210311', b'210311 New Zealand History'),
                            (b'210312', b'210312 North American History'),
                            (
                                b'210313',
                                b'210313 Pacific History (excl. New Zealand and Maori)',
                            ),
                            (
                                b'210399',
                                b'210399 Historical Studies not elsewhere classified',
                            ),
                            (b'2199', b'2199 OTHER HISTORY AND ARCHAEOLOGY'),
                            (
                                b'219999',
                                b'219999 History and Archaeology not elsewhere classified',
                            ),
                            (b'22', b'22 PHILOSOPHY AND RELIGIOUS STUDIES'),
                            (b'2201', b'2201 APPLIED ETHICS'),
                            (
                                b'220101',
                                b'220101 Bioethics (human and animal)',
                            ),
                            (b'220102', b'220102 Business Ethics'),
                            (
                                b'220103',
                                b'220103 Ethical Use of New Technology (e.g. Nanotechnology, Biotechnology)',
                            ),
                            (
                                b'220104',
                                b'220104 Human Rights and Justice Issues',
                            ),
                            (b'220105', b'220105 Legal Ethics'),
                            (b'220106', b'220106 Medical Ethics'),
                            (
                                b'220107',
                                b'220107 Professional Ethics (incl. police and research ethics)',
                            ),
                            (
                                b'220199',
                                b'220199 Applied Ethics not elsewhere classified',
                            ),
                            (
                                b'2202',
                                b'2202 HISTORY AND PHILOSOPHY OF SPECIFIC FIELDS',
                            ),
                            (b'220201', b'220201 Business and Labour History'),
                            (
                                b'220202',
                                b'220202 History and Philosophy of Education',
                            ),
                            (
                                b'220203',
                                b'220203 History and Philosophy of Engineering and Technology',
                            ),
                            (
                                b'220204',
                                b'220204 History and Philosophy of Law and Justice',
                            ),
                            (
                                b'220205',
                                b'220205 History and Philosophy of Medicine',
                            ),
                            (
                                b'220206',
                                b'220206 History and Philosophy of Science (incl. Non-historical Philosophy of Science)',
                            ),
                            (
                                b'220207',
                                b'220207 History and Philosophy of the Humanities',
                            ),
                        ],
                    ),
                ),
                (
                    'for_percentage_1',
                    models.IntegerField(
                        default=100,
                        help_text=b'The percentage',
                        choices=[
                            (0, b'0%'),
                            (10, b'10%'),
                            (20, b'20%'),
                            (30, b'30%'),
                            (40, b'40%'),
                            (50, b'50%'),
                            (60, b'60%'),
                            (70, b'70%'),
                            (80, b'80%'),
                            (90, b'90%'),
                            (100, b'100%'),
                        ],
                    ),
                ),
                (
                    'field_of_research_2',
                    models.CharField(
                        blank=True,
                        max_length=6,
                        null=True,
                        verbose_name=b'Second Field Of Research',
                        choices=[
                            (b'01', b'01 MATHEMATICAL SCIENCES'),
                            (b'0101', b'0101 PURE MATHEMATICS'),
                            (b'010101', b'010101 Algebra and Number Theory'),
                            (
                                b'010102',
                                b'010102 Algebraic and Differential Geometry',
                            ),
                            (
                                b'010103',
                                b'010103 Category Theory, K Theory, Homological Algebra',
                            ),
                            (
                                b'010104',
                                b'010104 Combinatorics and Discrete Mathematics (excl. Physical Combinatorics)',
                            ),
                            (
                                b'010105',
                                b'010105 Group Theory and Generalisations',
                            ),
                            (
                                b'010106',
                                b'010106 Lie Groups, Harmonic and Fourier Analysis',
                            ),
                            (
                                b'010107',
                                b'010107 Mathematical Logic, Set Theory, Lattices and Universal Algebra',
                            ),
                            (
                                b'010108',
                                b'010108 Operator Algebras and Functional Analysis',
                            ),
                            (
                                b'010109',
                                b'010109 Ordinary Differential Equations, Difference Equations and Dynamical Systems',
                            ),
                            (
                                b'010110',
                                b'010110 Partial Differential Equations',
                            ),
                            (
                                b'010111',
                                b'010111 Real and Complex Functions (incl. Several Variables)',
                            ),
                            (b'010112', b'010112 Topology'),
                            (
                                b'010199',
                                b'010199 Pure Mathematics not elsewhere classified',
                            ),
                            (b'0102', b'0102 APPLIED MATHEMATICS'),
                            (
                                b'010201',
                                b'010201 Approximation Theory and Asymptotic Methods',
                            ),
                            (b'010202', b'010202 Biological Mathematics'),
                            (
                                b'010203',
                                b'010203 Calculus of Variations, Systems Theory and Control Theory',
                            ),
                            (
                                b'010204',
                                b'010204 Dynamical Systems in Applications',
                            ),
                            (b'010205', b'010205 Financial Mathematics'),
                            (b'010206', b'010206 Operations Research'),
                            (
                                b'010207',
                                b'010207 Theoretical and Applied Mechanics',
                            ),
                            (
                                b'010299',
                                b'010299 Applied Mathematics not elsewhere classified',
                            ),
                            (
                                b'0103',
                                b'0103 NUMERICAL AND COMPUTATIONAL MATHEMATICS',
                            ),
                            (b'010301', b'010301 Numerical Analysis'),
                            (
                                b'010302',
                                b'010302 Numerical Solution of Differential and Integral Equations',
                            ),
                            (b'010303', b'010303 Optimisation'),
                            (
                                b'010399',
                                b'010399 Numerical and Computational Mathematics not elsewhere classified',
                            ),
                            (b'0104', b'0104 STATISTICS'),
                            (b'010401', b'010401 Applied Statistics'),
                            (b'010402', b'010402 Biostatistics'),
                            (b'010403', b'010403 Forensic Statistics'),
                            (b'010404', b'010404 Probability Theory'),
                            (b'010405', b'010405 Statistical Theory'),
                            (
                                b'010406',
                                b'010406 Stochastic Analysis and Modelling',
                            ),
                            (
                                b'010499',
                                b'010499 Statistics not elsewhere classified',
                            ),
                            (b'0105', b'0105 MATHEMATICAL PHYSICS'),
                            (
                                b'010501',
                                b'010501 Algebraic Structures in Mathematical Physics',
                            ),
                            (
                                b'010502',
                                b'010502 Integrable Systems (Classical and Quantum)',
                            ),
                            (
                                b'010503',
                                b'010503 Mathematical Aspects of Classical Mechanics, Quantum Mechanics and Quantum Information Theory',
                            ),
                            (
                                b'010504',
                                b'010504 Mathematical Aspects of General Relativity',
                            ),
                            (
                                b'010505',
                                b'010505 Mathematical Aspects of Quantum and Conformal Field Theory, Quantum Gravity and String Theory',
                            ),
                            (
                                b'010506',
                                b'010506 Statistical Mechanics, Physical Combinatorics and Mathematical Aspects of Condensed Matter',
                            ),
                            (
                                b'010599',
                                b'010599 Mathematical Physics not elsewhere classified',
                            ),
                            (b'0199', b'0199 OTHER MATHEMATICAL SCIENCES'),
                            (
                                b'019999',
                                b'019999 Mathematical Sciences not elsewhere classified',
                            ),
                            (b'02', b'02 PHYSICAL SCIENCES'),
                            (b'0201', b'0201 ASTRONOMICAL AND SPACE SCIENCES'),
                            (b'020101', b'020101 Astrobiology'),
                            (
                                b'020102',
                                b'020102 Astronomical and Space Instrumentation',
                            ),
                            (
                                b'020103',
                                b'020103 Cosmology and Extragalactic Astronomy',
                            ),
                            (b'020104', b'020104 Galactic Astronomy'),
                            (
                                b'020105',
                                b'020105 General Relativity and Gravitational Waves',
                            ),
                            (
                                b'020106',
                                b'020106 High Energy Astrophysics; Cosmic Rays',
                            ),
                            (
                                b'020107',
                                b'020107 Mesospheric, Ionospheric and Magnetospheric Physics',
                            ),
                            (
                                b'020108',
                                b'020108 Planetary Science (excl. Extraterrestrial Geology)',
                            ),
                            (b'020109', b'020109 Space and Solar Physics'),
                            (
                                b'020110',
                                b'020110 Stellar Astronomy and Planetary Systems',
                            ),
                            (
                                b'020199',
                                b'020199 Astronomical and Space Sciences not elsewhere classified',
                            ),
                            (
                                b'0202',
                                b'0202 ATOMIC, MOLECULAR, NUCLEAR, PARTICLE AND PLASMA PHYSICS',
                            ),
                            (
                                b'020201',
                                b'020201 Atomic and Molecular Physics',
                            ),
                            (b'020202', b'020202 Nuclear Physics'),
                            (b'020203', b'020203 Particle Physics'),
                            (
                                b'020204',
                                b'020204 Plasma Physics; Fusion Plasmas; Electrical Discharges',
                            ),
                            (
                                b'020299',
                                b'020299 Atomic, Molecular, Nuclear, Particle and Plasma Physics not elsewhere classified',
                            ),
                            (b'0203', b'0203 CLASSICAL PHYSICS'),
                            (
                                b'020301',
                                b'020301 Acoustics and Acoustical Devices; Waves',
                            ),
                            (
                                b'020302',
                                b'020302 Electrostatics and Electrodynamics',
                            ),
                            (b'020303', b'020303 Fluid Physics'),
                            (
                                b'020304',
                                b'020304 Thermodynamics and Statistical Physics',
                            ),
                            (
                                b'020399',
                                b'020399 Classical Physics not elsewhere classified',
                            ),
                            (b'0204', b'0204 CONDENSED MATTER PHYSICS'),
                            (
                                b'020401',
                                b'020401 Condensed Matter Characterisation Technique Development',
                            ),
                            (b'020402', b'020402 Condensed Matter Imaging'),
                            (
                                b'020403',
                                b'020403 Condensed Matter Modelling and Density Functional Theory',
                            ),
                            (
                                b'020404',
                                b'020404 Electronic and Magnetic Properties of Condensed Matter; Superconductivity',
                            ),
                            (b'020405', b'020405 Soft Condensed Matter'),
                            (
                                b'020406',
                                b'020406 Surfaces and Structural Properties of Condensed Matter',
                            ),
                            (
                                b'020499',
                                b'020499 Condensed Matter Physics not elsewhere classified',
                            ),
                            (b'0205', b'0205 OPTICAL PHYSICS'),
                            (
                                b'020501',
                                b'020501 Classical and Physical Optics',
                            ),
                            (
                                b'020502',
                                b'020502 Lasers and Quantum Electronics',
                            ),
                            (
                                b'020503',
                                b'020503 Nonlinear Optics and Spectroscopy',
                            ),
                            (
                                b'020504',
                                b'020504 Photonics, Optoelectronics and Optical Communications',
                            ),
                            (
                                b'020599',
                                b'020599 Optical Physics not elsewhere classified',
                            ),
                            (b'0206', b'0206 QUANTUM PHYSICS'),
                            (
                                b'020601',
                                b'020601 Degenerate Quantum Gases and Atom Optics',
                            ),
                            (
                                b'020602',
                                b'020602 Field Theory and String Theory',
                            ),
                            (
                                b'020603',
                                b'020603 Quantum Information, Computation and Communication',
                            ),
                            (b'020604', b'020604 Quantum Optics'),
                            (
                                b'020699',
                                b'020699 Quantum Physics not elsewhere classified',
                            ),
                            (b'0299', b'0299 OTHER PHYSICAL SCIENCES'),
                            (b'029901', b'029901 Biological Physics'),
                            (b'029902', b'029902 Complex Physical Systems'),
                            (b'029903', b'029903 Medical Physics'),
                            (
                                b'029904',
                                b'029904 Synchrotrons; Accelerators; Instruments and Techniques',
                            ),
                            (
                                b'029999',
                                b'029999 Physical Sciences not elsewhere classified',
                            ),
                            (b'03', b'03 CHEMICAL SCIENCES'),
                            (b'0301', b'0301 ANALYTICAL CHEMISTRY'),
                            (b'030101', b'030101 Analytical Spectrometry'),
                            (b'030102', b'030102 Electroanalytical Chemistry'),
                            (b'030103', b'030103 Flow Analysis'),
                            (
                                b'030104',
                                b'030104 Immunological and Bioassay Methods',
                            ),
                            (
                                b'030105',
                                b'030105 Instrumental Methods (excl. Immunological and Bioassay Methods)',
                            ),
                            (
                                b'030106',
                                b'030106 Quality Assurance, Chemometrics, Traceability and Metrological Chemistry',
                            ),
                            (
                                b'030107',
                                b'030107 Sensor Technology (Chemical aspects)',
                            ),
                            (b'030108', b'030108 Separation Science'),
                            (
                                b'030199',
                                b'030199 Analytical Chemistry not elsewhere classified',
                            ),
                            (b'0302', b'0302 INORGANIC CHEMISTRY'),
                            (b'030201', b'030201 Bioinorganic Chemistry'),
                            (b'030202', b'030202 f-Block Chemistry'),
                            (b'030203', b'030203 Inorganic Green Chemistry'),
                            (b'030204', b'030204 Main Group Metal Chemistry'),
                            (b'030205', b'030205 Non-metal Chemistry'),
                            (b'030206', b'030206 Solid State Chemistry'),
                            (b'030207', b'030207 Transition Metal Chemistry'),
                            (
                                b'030299',
                                b'030299 Inorganic Chemistry not elsewhere classified',
                            ),
                            (
                                b'0303',
                                b'0303 MACROMOLECULAR AND MATERIALS CHEMISTRY',
                            ),
                            (
                                b'030301',
                                b'030301 Chemical Characterisation of Materials',
                            ),
                            (
                                b'030302',
                                b'030302 Nanochemistry and Supramolecular Chemistry',
                            ),
                            (
                                b'030303',
                                b'030303 Optical Properties of Materials',
                            ),
                            (
                                b'030304',
                                b'030304 Physical Chemistry of Materials',
                            ),
                            (b'030305', b'030305 Polymerisation Mechanisms'),
                            (b'030306', b'030306 Synthesis of Materials'),
                            (
                                b'030307',
                                b'030307 Theory and Design of Materials',
                            ),
                            (
                                b'030399',
                                b'030399 Macromolecular and Materials Chemistry not elsewhere classified',
                            ),
                            (
                                b'0304',
                                b'0304 MEDICINAL AND BIOMOLECULAR CHEMISTRY',
                            ),
                            (
                                b'030401',
                                b'030401 Biologically Active Molecules',
                            ),
                            (
                                b'030402',
                                b'030402 Biomolecular Modelling and Design',
                            ),
                            (
                                b'030403',
                                b'030403 Characterisation of Biological Macromolecules',
                            ),
                            (
                                b'030404',
                                b'030404 Cheminformatics and Quantitative Structure-Activity Relationships',
                            ),
                            (b'030405', b'030405 Molecular Medicine'),
                            (b'030406', b'030406 Proteins and Peptides'),
                            (
                                b'030499',
                                b'030499 Medicinal and Biomolecular Chemistry not elsewhere classified',
                            ),
                            (b'0305', b'0305 ORGANIC CHEMISTRY'),
                            (b'030501', b'030501 Free Radical Chemistry'),
                            (b'030502', b'030502 Natural Products Chemistry'),
                            (b'030503', b'030503 Organic Chemical Synthesis'),
                            (b'030504', b'030504 Organic Green Chemistry'),
                            (b'030505', b'030505 Physical Organic Chemistry'),
                            (
                                b'030599',
                                b'030599 Organic Chemistry not elsewhere classified',
                            ),
                            (
                                b'0306',
                                b'0306 PHYSICAL CHEMISTRY (INCL. STRUCTURAL)',
                            ),
                            (
                                b'030601',
                                b'030601 Catalysis and Mechanisms of Reactions',
                            ),
                            (
                                b'030602',
                                b'030602 Chemical Thermodynamics and Energetics',
                            ),
                            (
                                b'030603',
                                b'030603 Colloid and Surface Chemistry',
                            ),
                            (b'030604', b'030604 Electrochemistry'),
                            (b'030605', b'030605 Solution Chemistry'),
                            (
                                b'030606',
                                b'030606 Structural Chemistry and Spectroscopy',
                            ),
                            (
                                b'030607',
                                b'030607 Transport Properties and Non-equilibrium Processes',
                            ),
                            (
                                b'030699',
                                b'030699 Physical Chemistry not elsewhere classified',
                            ),
                            (
                                b'0307',
                                b'0307 THEORETICAL AND COMPUTATIONAL CHEMISTRY',
                            ),
                            (b'030701', b'030701 Quantum Chemistry'),
                            (b'030702', b'030702 Radiation and Matter'),
                            (
                                b'030703',
                                b'030703 Reaction Kinetics and Dynamics',
                            ),
                            (
                                b'030704',
                                b'030704 Statistical Mechanics in Chemistry',
                            ),
                            (
                                b'030799',
                                b'030799 Theoretical and Computational Chemistry not elsewhere classified',
                            ),
                            (b'0399', b'0399 OTHER CHEMICAL SCIENCES'),
                            (
                                b'039901',
                                b'039901 Environmental Chemistry (incl. Atmospheric Chemistry)',
                            ),
                            (b'039902', b'039902 Forensic Chemistry'),
                            (b'039903', b'039903 Industrial Chemistry'),
                            (b'039904', b'039904 Organometallic Chemistry'),
                            (
                                b'039999',
                                b'039999 Chemical Sciences not elsewhere classified',
                            ),
                            (b'04', b'04 EARTH SCIENCES'),
                            (b'0401', b'0401 ATMOSPHERIC SCIENCES'),
                            (b'040101', b'040101 Atmospheric Aerosols'),
                            (b'040102', b'040102 Atmospheric Dynamics'),
                            (b'040103', b'040103 Atmospheric Radiation'),
                            (b'040104', b'040104 Climate Change Processes'),
                            (
                                b'040105',
                                b'040105 Climatology (excl. Climate Change Processes)',
                            ),
                            (b'040106', b'040106 Cloud Physics'),
                            (b'040107', b'040107 Meteorology'),
                            (
                                b'040108',
                                b'040108 Tropospheric and Stratospheric Physics',
                            ),
                            (
                                b'040199',
                                b'040199 Atmospheric Sciences not elsewhere classified',
                            ),
                            (b'0402', b'0402 GEOCHEMISTRY'),
                            (b'040201', b'040201 Exploration Geochemistry'),
                            (b'040202', b'040202 Inorganic Geochemistry'),
                            (b'040203', b'040203 Isotope Geochemistry'),
                            (b'040204', b'040204 Organic Geochemistry'),
                            (
                                b'040299',
                                b'040299 Geochemistry not elsewhere classified',
                            ),
                            (b'0403', b'0403 GEOLOGY'),
                            (b'040301', b'040301 Basin Analysis'),
                            (b'040302', b'040302 Extraterrestrial Geology'),
                            (b'040303', b'040303 Geochronology'),
                            (
                                b'040304',
                                b'040304 Igneous and Metamorphic Petrology',
                            ),
                            (b'040305', b'040305 Marine Geoscience'),
                            (
                                b'040306',
                                b'040306 Mineralogy and Crystallography',
                            ),
                            (b'040307', b'040307 Ore Deposit Petrology'),
                            (
                                b'040308',
                                b'040308 Palaeontology (incl. Palynology)',
                            ),
                            (b'040309', b'040309 Petroleum and Coal Geology'),
                            (b'040310', b'040310 Sedimentology'),
                            (
                                b'040311',
                                b'040311 Stratigraphy (incl. Biostratigraphy and Sequence Stratigraphy)',
                            ),
                            (b'040312', b'040312 Structural Geology'),
                            (b'040313', b'040313 Tectonics'),
                            (b'040314', b'040314 Volcanology'),
                            (
                                b'040399',
                                b'040399 Geology not elsewhere classified',
                            ),
                            (b'0404', b'0404 GEOPHYSICS'),
                            (
                                b'040401',
                                b'040401 Electrical and Electromagnetic Methods in Geophysics',
                            ),
                            (b'040402', b'040402 Geodynamics'),
                            (b'040403', b'040403 Geophysical Fluid Dynamics'),
                            (
                                b'040404',
                                b'040404 Geothermics and Radiometrics',
                            ),
                            (b'040405', b'040405 Gravimetrics'),
                            (
                                b'040406',
                                b'040406 Magnetism and Palaeomagnetism',
                            ),
                            (
                                b'040407',
                                b'040407 Seismology and Seismic Exploration',
                            ),
                            (
                                b'040499',
                                b'040499 Geophysics not elsewhere classified',
                            ),
                            (b'0405', b'0405 OCEANOGRAPHY'),
                            (b'040501', b'040501 Biological Oceanography'),
                            (b'040502', b'040502 Chemical Oceanography'),
                            (b'040503', b'040503 Physical Oceanography'),
                            (
                                b'040599',
                                b'040599 Oceanography not elsewhere classified',
                            ),
                            (
                                b'0406',
                                b'0406 PHYSICAL GEOGRAPHY AND ENVIRONMENTAL GEOSCIENCE',
                            ),
                            (
                                b'040601',
                                b'040601 Geomorphology and Regolith and Landscape Evolution',
                            ),
                            (b'040602', b'040602 Glaciology'),
                            (b'040603', b'040603 Hydrogeology'),
                            (b'040604', b'040604 Natural Hazards'),
                            (b'040605', b'040605 Palaeoclimatology'),
                            (b'040606', b'040606 Quaternary Environments'),
                            (b'040607', b'040607 Surface Processes'),
                            (b'040608', b'040608 Surfacewater Hydrology'),
                            (
                                b'040699',
                                b'040699 Physical Geography and Environmental Geoscience not elsewhere classified',
                            ),
                            (b'0499', b'0499 OTHER EARTH SCIENCES'),
                            (
                                b'049999',
                                b'049999 Earth Sciences not elsewhere classified',
                            ),
                            (b'05', b'05 ENVIRONMENTAL SCIENCES'),
                            (b'0501', b'0501 ECOLOGICAL APPLICATIONS'),
                            (
                                b'050101',
                                b'050101 Ecological Impacts of Climate Change',
                            ),
                            (b'050102', b'050102 Ecosystem Function'),
                            (b'050103', b'050103 Invasive Species Ecology'),
                            (b'050104', b'050104 Landscape Ecology'),
                            (
                                b'050199',
                                b'050199 Ecological Applications not elsewhere classified',
                            ),
                            (
                                b'0502',
                                b'0502 ENVIRONMENTAL SCIENCE AND MANAGEMENT',
                            ),
                            (
                                b'050201',
                                b'050201 Aboriginal and Torres Strait Islander Environmental Knowledge',
                            ),
                            (
                                b'050202',
                                b'050202 Conservation and Biodiversity',
                            ),
                            (
                                b'050203',
                                b'050203 Environmental Education and Extension',
                            ),
                            (
                                b'050204',
                                b'050204 Environmental Impact Assessment',
                            ),
                            (b'050205', b'050205 Environmental Management'),
                            (b'050206', b'050206 Environmental Monitoring'),
                            (
                                b'050207',
                                b'050207 Environmental Rehabilitation (excl. Bioremediation)',
                            ),
                            (
                                b'050208',
                                b'050208 Maori Environmental Knowledge',
                            ),
                            (b'050209', b'050209 Natural Resource Management'),
                            (
                                b'050210',
                                b'050210 Pacific Peoples Environmental Knowledge',
                            ),
                            (
                                b'050211',
                                b'050211 Wildlife and Habitat Management',
                            ),
                            (
                                b'050299',
                                b'050299 Environmental Science and Management not elsewhere classified',
                            ),
                            (b'0503', b'0503 SOIL SCIENCES'),
                            (
                                b'050301',
                                b'050301 Carbon Sequestration Science',
                            ),
                            (
                                b'050302',
                                b'050302 Land Capability and Soil Degradation',
                            ),
                            (b'050303', b'050303 Soil Biology'),
                            (
                                b'050304',
                                b'050304 Soil Chemistry (excl. Carbon Sequestration Science)',
                            ),
                            (b'050305', b'050305 Soil Physics'),
                            (
                                b'050399',
                                b'050399 Soil Sciences not elsewhere classified',
                            ),
                            (b'0599', b'0599 OTHER ENVIRONMENTAL SCIENCES'),
                            (
                                b'059999',
                                b'059999 Environmental Sciences not elsewhere classified',
                            ),
                            (b'06', b'06 BIOLOGICAL SCIENCES'),
                            (b'0601', b'0601 BIOCHEMISTRY AND CELL BIOLOGY'),
                            (b'060101', b'060101 Analytical Biochemistry'),
                            (b'060102', b'060102 Bioinformatics'),
                            (
                                b'060103',
                                b'060103 Cell Development, Proliferation and Death',
                            ),
                            (b'060104', b'060104 Cell Metabolism'),
                            (b'060105', b'060105 Cell Neurochemistry'),
                            (
                                b'060106',
                                b'060106 Cellular Interactions (incl. Adhesion, Matrix, Cell Wall)',
                            ),
                            (b'060107', b'060107 Enzymes'),
                            (b'060108', b'060108 Protein Trafficking'),
                            (
                                b'060109',
                                b'060109 Proteomics and Intermolecular Interactions (excl. Medical Proteomics)',
                            ),
                            (
                                b'060110',
                                b'060110 Receptors and Membrane Biology',
                            ),
                            (b'060111', b'060111 Signal Transduction'),
                            (
                                b'060112',
                                b'060112 Structural Biology (incl. Macromolecular Modelling)',
                            ),
                            (b'060113', b'060113 Synthetic Biology'),
                            (b'060114', b'060114 Systems Biology'),
                            (
                                b'060199',
                                b'060199 Biochemistry and Cell Biology not elsewhere classified',
                            ),
                            (b'0602', b'0602 ECOLOGY'),
                            (b'060201', b'060201 Behavioural Ecology'),
                            (
                                b'060202',
                                b'060202 Community Ecology (excl. Invasive Species Ecology)',
                            ),
                            (b'060203', b'060203 Ecological Physiology'),
                            (b'060204', b'060204 Freshwater Ecology'),
                            (
                                b'060205',
                                b'060205 Marine and Estuarine Ecology (incl. Marine Ichthyology)',
                            ),
                            (b'060206', b'060206 Palaeoecology'),
                            (b'060207', b'060207 Population Ecology'),
                            (b'060208', b'060208 Terrestrial Ecology'),
                            (
                                b'060299',
                                b'060299 Ecology not elsewhere classified',
                            ),
                            (b'0603', b'0603 EVOLUTIONARY BIOLOGY'),
                            (
                                b'060301',
                                b'060301 Animal Systematics and Taxonomy',
                            ),
                            (
                                b'060302',
                                b'060302 Biogeography and Phylogeography',
                            ),
                            (b'060303', b'060303 Biological Adaptation'),
                            (b'060304', b'060304 Ethology and Sociobiology'),
                            (
                                b'060305',
                                b'060305 Evolution of Developmental Systems',
                            ),
                            (
                                b'060306',
                                b'060306 Evolutionary Impacts of Climate Change',
                            ),
                            (b'060307', b'060307 Host-Parasite Interactions'),
                            (b'060308', b'060308 Life Histories'),
                            (
                                b'060309',
                                b'060309 Phylogeny and Comparative Analysis',
                            ),
                            (
                                b'060310',
                                b'060310 Plant Systematics and Taxonomy',
                            ),
                            (b'060311', b'060311 Speciation and Extinction'),
                            (
                                b'060399',
                                b'060399 Evolutionary Biology not elsewhere classified',
                            ),
                            (b'0604', b'0604 GENETICS'),
                            (b'060401', b'060401 Anthropological Genetics'),
                            (b'060402', b'060402 Cell and Nuclear Division'),
                            (
                                b'060403',
                                b'060403 Developmental Genetics (incl. Sex Determination)',
                            ),
                            (
                                b'060404',
                                b'060404 Epigenetics (incl. Genome Methylation and Epigenomics)',
                            ),
                            (
                                b'060405',
                                b'060405 Gene Expression (incl. Microarray and other genome-wide approaches)',
                            ),
                            (b'060406', b'060406 Genetic Immunology'),
                            (
                                b'060407',
                                b'060407 Genome Structure and Regulation',
                            ),
                            (b'060408', b'060408 Genomics'),
                            (b'060409', b'060409 Molecular Evolution'),
                            (b'060410', b'060410 Neurogenetics'),
                            (
                                b'060411',
                                b'060411 Population, Ecological and Evolutionary Genetics',
                            ),
                            (
                                b'060412',
                                b'060412 Quantitative Genetics (incl. Disease and Trait Mapping Genetics)',
                            ),
                            (
                                b'060499',
                                b'060499 Genetics not elsewhere classified',
                            ),
                            (b'0605', b'0605 MICROBIOLOGY'),
                            (b'060501', b'060501 Bacteriology'),
                            (b'060502', b'060502 Infectious Agents'),
                            (b'060503', b'060503 Microbial Genetics'),
                            (b'060504', b'060504 Microbial Ecology'),
                            (b'060505', b'060505 Mycology'),
                            (b'060506', b'060506 Virology'),
                            (
                                b'060599',
                                b'060599 Microbiology not elsewhere classified',
                            ),
                            (b'0606', b'0606 PHYSIOLOGY'),
                            (
                                b'060601',
                                b'060601 Animal Physiology - Biophysics',
                            ),
                            (b'060602', b'060602 Animal Physiology - Cell'),
                            (b'060603', b'060603 Animal Physiology - Systems'),
                            (b'060604', b'060604 Comparative Physiology'),
                            (
                                b'060699',
                                b'060699 Physiology not elsewhere classified',
                            ),
                            (b'0607', b'0607 PLANT BIOLOGY'),
                            (
                                b'060701',
                                b'060701 Phycology (incl. Marine Grasses)',
                            ),
                            (
                                b'060702',
                                b'060702 Plant Cell and Molecular Biology',
                            ),
                            (
                                b'060703',
                                b'060703 Plant Developmental and Reproductive Biology',
                            ),
                            (b'060704', b'060704 Plant Pathology'),
                            (b'060705', b'060705 Plant Physiology'),
                            (
                                b'060799',
                                b'060799 Plant Biology not elsewhere classified',
                            ),
                            (b'0608', b'0608 ZOOLOGY'),
                            (b'060801', b'060801 Animal Behaviour'),
                            (
                                b'060802',
                                b'060802 Animal Cell and Molecular Biology',
                            ),
                            (
                                b'060803',
                                b'060803 Animal Developmental and Reproductive Biology',
                            ),
                            (b'060804', b'060804 Animal Immunology'),
                            (b'060805', b'060805 Animal Neurobiology'),
                            (
                                b'060806',
                                b'060806 Animal Physiological Ecology',
                            ),
                            (
                                b'060807',
                                b'060807 Animal Structure and Function',
                            ),
                            (b'060808', b'060808 Invertebrate Biology'),
                            (b'060809', b'060809 Vertebrate Biology'),
                            (
                                b'060899',
                                b'060899 Zoology not elsewhere classified',
                            ),
                            (b'0699', b'0699 OTHER BIOLOGICAL SCIENCES'),
                            (b'069901', b'069901 Forensic Biology'),
                            (b'069902', b'069902 Global Change Biology'),
                            (
                                b'069999',
                                b'069999 Biological Sciences not elsewhere classified',
                            ),
                            (
                                b'07',
                                b'07 AGRICULTURAL AND VETERINARY SCIENCES',
                            ),
                            (
                                b'0701',
                                b'0701 AGRICULTURE, LAND AND FARM MANAGEMENT',
                            ),
                            (
                                b'070101',
                                b'070101 Agricultural Land Management',
                            ),
                            (b'070102', b'070102 Agricultural Land Planning'),
                            (
                                b'070103',
                                b'070103 Agricultural Production Systems Simulation',
                            ),
                            (
                                b'070104',
                                b'070104 Agricultural Spatial Analysis and Modelling',
                            ),
                            (
                                b'070105',
                                b'070105 Agricultural Systems Analysis and Modelling',
                            ),
                            (
                                b'070106',
                                b'070106 Farm Management, Rural Management and Agribusiness',
                            ),
                            (b'070107', b'070107 Farming Systems Research'),
                            (
                                b'070108',
                                b'070108 Sustainable Agricultural Development',
                            ),
                            (
                                b'070199',
                                b'070199 Agriculture, Land and Farm Management not elsewhere classified',
                            ),
                            (b'0702', b'0702 ANIMAL PRODUCTION'),
                            (b'070201', b'070201 Animal Breeding'),
                            (
                                b'070202',
                                b'070202 Animal Growth and Development',
                            ),
                            (b'070203', b'070203 Animal Management'),
                            (b'070204', b'070204 Animal Nutrition'),
                            (
                                b'070205',
                                b'070205 Animal Protection (Pests and Pathogens)',
                            ),
                            (b'070206', b'070206 Animal Reproduction'),
                            (b'070207', b'070207 Humane Animal Treatment'),
                            (
                                b'070299',
                                b'070299 Animal Production not elsewhere classified',
                            ),
                            (b'0703', b'0703 CROP AND PASTURE PRODUCTION'),
                            (
                                b'070301',
                                b'070301 Agro-ecosystem Function and Prediction',
                            ),
                            (b'070302', b'070302 Agronomy'),
                            (
                                b'070303',
                                b'070303 Crop and Pasture Biochemistry and Physiology',
                            ),
                            (
                                b'070304',
                                b'070304 Crop and Pasture Biomass and Bioproducts',
                            ),
                            (
                                b'070305',
                                b'070305 Crop and Pasture Improvement (Selection and Breeding)',
                            ),
                            (b'070306', b'070306 Crop and Pasture Nutrition'),
                            (
                                b'070307',
                                b'070307 Crop and Pasture Post Harvest Technologies (incl. Transportation and Storage)',
                            ),
                            (
                                b'070308',
                                b'070308 Crop and Pasture Protection (Pests, Diseases and Weeds)',
                            ),
                            (
                                b'070399',
                                b'070399 Crop and Pasture Production not elsewhere classified',
                            ),
                            (b'0704', b'0704 FISHERIES SCIENCES'),
                            (b'070401', b'070401 Aquaculture'),
                            (
                                b'070402',
                                b'070402 Aquatic Ecosystem Studies and Stock Assessment',
                            ),
                            (b'070403', b'070403 Fisheries Management'),
                            (b'070404', b'070404 Fish Pests and Diseases'),
                            (
                                b'070405',
                                b'070405 Fish Physiology and Genetics',
                            ),
                            (
                                b'070406',
                                b'070406 Post-Harvest Fisheries Technologies (incl. Transportation)',
                            ),
                            (
                                b'070499',
                                b'070499 Fisheries Sciences not elsewhere classified',
                            ),
                            (b'0705', b'0705 FORESTRY SCIENCES'),
                            (b'070501', b'070501 Agroforestry'),
                            (
                                b'070502',
                                b'070502 Forestry Biomass and Bioproducts',
                            ),
                            (b'070503', b'070503 Forestry Fire Management'),
                            (
                                b'070504',
                                b'070504 Forestry Management and Environment',
                            ),
                            (
                                b'070505',
                                b'070505 Forestry Pests, Health and Diseases',
                            ),
                            (
                                b'070506',
                                b'070506 Forestry Product Quality Assessment',
                            ),
                            (
                                b'070507',
                                b'070507 Tree Improvement (Selection and Breeding)',
                            ),
                            (
                                b'070508',
                                b'070508 Tree Nutrition and Physiology',
                            ),
                            (b'070509', b'070509 Wood Fibre Processing'),
                            (b'070510', b'070510 Wood Processing'),
                            (
                                b'070599',
                                b'070599 Forestry Sciences not elsewhere classified',
                            ),
                            (b'0706', b'0706 HORTICULTURAL PRODUCTION'),
                            (
                                b'070601',
                                b'070601 Horticultural Crop Growth and Development',
                            ),
                            (
                                b'070602',
                                b'070602 Horticultural Crop Improvement (Selection and Breeding)',
                            ),
                            (
                                b'070603',
                                b'070603 Horticultural Crop Protection (Pests, Diseases and Weeds)',
                            ),
                            (b'070604', b'070604 Oenology and Viticulture'),
                            (
                                b'070605',
                                b'070605 Post Harvest Horticultural Technologies (incl. Transportation and Storage)',
                            ),
                            (
                                b'070699',
                                b'070699 Horticultural Production not elsewhere classified',
                            ),
                            (b'0707', b'0707 VETERINARY SCIENCES'),
                            (
                                b'070701',
                                b'070701 Veterinary Anaesthesiology and Intensive Care',
                            ),
                            (
                                b'070702',
                                b'070702 Veterinary Anatomy and Physiology',
                            ),
                            (
                                b'070703',
                                b'070703 Veterinary Diagnosis and Diagnostics',
                            ),
                            (b'070704', b'070704 Veterinary Epidemiology'),
                            (b'070705', b'070705 Veterinary Immunology'),
                            (b'070706', b'070706 Veterinary Medicine'),
                            (
                                b'070707',
                                b'070707 Veterinary Microbiology (excl. Virology)',
                            ),
                            (b'070708', b'070708 Veterinary Parasitology'),
                            (b'070709', b'070709 Veterinary Pathology'),
                            (b'070710', b'070710 Veterinary Pharmacology'),
                            (b'070711', b'070711 Veterinary Surgery'),
                            (b'070712', b'070712 Veterinary Virology'),
                            (
                                b'070799',
                                b'070799 Veterinary Sciences not elsewhere classified',
                            ),
                            (
                                b'0799',
                                b'0799 OTHER AGRICULTURAL AND VETERINARY SCIENCES',
                            ),
                            (
                                b'079901',
                                b'079901 Agricultural Hydrology (Drainage, Flooding, Irrigation, Quality, etc.)',
                            ),
                            (
                                b'079902',
                                b'079902 Fertilisers and Agrochemicals (incl. Application)',
                            ),
                            (
                                b'079999',
                                b'079999 Agricultural and Veterinary Sciences not elsewhere classified',
                            ),
                            (b'08', b'08 INFORMATION AND COMPUTING SCIENCES'),
                            (
                                b'0801',
                                b'0801 ARTIFICIAL INTELLIGENCE AND IMAGE PROCESSING',
                            ),
                            (
                                b'080101',
                                b'080101 Adaptive Agents and Intelligent Robotics',
                            ),
                            (b'080102', b'080102 Artificial Life'),
                            (b'080103', b'080103 Computer Graphics'),
                            (b'080104', b'080104 Computer Vision'),
                            (b'080105', b'080105 Expert Systems'),
                            (b'080106', b'080106 Image Processing'),
                            (b'080107', b'080107 Natural Language Processing'),
                            (
                                b'080108',
                                b'080108 Neural, Evolutionary and Fuzzy Computation',
                            ),
                            (
                                b'080109',
                                b'080109 Pattern Recognition and Data Mining',
                            ),
                            (b'080110', b'080110 Simulation and Modelling'),
                            (
                                b'080111',
                                b'080111 Virtual Reality and Related Simulation',
                            ),
                            (
                                b'080199',
                                b'080199 Artificial Intelligence and Image Processing not elsewhere classified',
                            ),
                            (
                                b'0802',
                                b'0802 COMPUTATION THEORY AND MATHEMATICS',
                            ),
                            (
                                b'080201',
                                b'080201 Analysis of Algorithms and Complexity',
                            ),
                            (
                                b'080202',
                                b'080202 Applied Discrete Mathematics',
                            ),
                            (
                                b'080203',
                                b'080203 Computational Logic and Formal Languages',
                            ),
                            (b'080204', b'080204 Mathematical Software'),
                            (b'080205', b'080205 Numerical Computation'),
                            (
                                b'080299',
                                b'080299 Computation Theory and Mathematics not elsewhere classified',
                            ),
                            (b'0803', b'0803 COMPUTER SOFTWARE'),
                            (b'080301', b'080301 Bioinformatics Software'),
                            (
                                b'080302',
                                b'080302 Computer System Architecture',
                            ),
                            (b'080303', b'080303 Computer System Security'),
                            (b'080304', b'080304 Concurrent Programming'),
                            (b'080305', b'080305 Multimedia Programming'),
                            (b'080306', b'080306 Open Software'),
                            (b'080307', b'080307 Operating Systems'),
                            (b'080308', b'080308 Programming Languages'),
                            (b'080309', b'080309 Software Engineering'),
                            (
                                b'080399',
                                b'080399 Computer Software not elsewhere classified',
                            ),
                            (b'0804', b'0804 DATA FORMAT'),
                            (
                                b'080401',
                                b'080401 Coding and Information Theory',
                            ),
                            (b'080402', b'080402 Data Encryption'),
                            (b'080403', b'080403 Data Structures'),
                            (b'080404', b'080404 Markup Languages'),
                            (
                                b'080499',
                                b'080499 Data Format not elsewhere classified',
                            ),
                            (b'0805', b'0805 DISTRIBUTED COMPUTING'),
                            (
                                b'080501',
                                b'080501 Distributed and Grid Systems',
                            ),
                            (b'080502', b'080502 Mobile Technologies'),
                            (
                                b'080503',
                                b'080503 Networking and Communications',
                            ),
                            (b'080504', b'080504 Ubiquitous Computing'),
                            (
                                b'080505',
                                b'080505 Web Technologies (excl. Web Search)',
                            ),
                            (
                                b'080599',
                                b'080599 Distributed Computing not elsewhere classified',
                            ),
                            (b'0806', b'0806 INFORMATION SYSTEMS'),
                            (
                                b'080601',
                                b'080601 Aboriginal and Torres Strait Islander Information and Knowledge Systems',
                            ),
                            (b'080602', b'080602 Computer-Human Interaction'),
                            (b'080603', b'080603 Conceptual Modelling'),
                            (b'080604', b'080604 Database Management'),
                            (
                                b'080605',
                                b'080605 Decision Support and Group Support Systems',
                            ),
                            (b'080606', b'080606 Global Information Systems'),
                            (
                                b'080607',
                                b'080607 Information Engineering and Theory',
                            ),
                            (
                                b'080608',
                                b'080608 Information Systems Development Methodologies',
                            ),
                            (
                                b'080609',
                                b'080609 Information Systems Management',
                            ),
                            (
                                b'080610',
                                b'080610 Information Systems Organisation',
                            ),
                            (b'080611', b'080611 Information Systems Theory'),
                            (
                                b'080612',
                                b'080612 Interorganisational Information Systems and Web Services',
                            ),
                            (
                                b'080613',
                                b'080613 Maori Information and Knowledge Systems',
                            ),
                            (
                                b'080614',
                                b'080614 Pacific Peoples Information and Knowledge Systems',
                            ),
                            (
                                b'080699',
                                b'080699 Information Systems not elsewhere classified',
                            ),
                            (b'0807', b'0807 LIBRARY AND INFORMATION STUDIES'),
                            (
                                b'080701',
                                b'080701 Aboriginal and Torres Strait Islander Knowledge Management',
                            ),
                            (b'080702', b'080702 Health Informatics'),
                            (b'080703', b'080703 Human Information Behaviour'),
                            (
                                b'080704',
                                b'080704 Information Retrieval and Web Search',
                            ),
                            (b'080705', b'080705 Informetrics'),
                            (b'080706', b'080706 Librarianship'),
                            (
                                b'080707',
                                b'080707 Organisation of Information and Knowledge Resources',
                            ),
                            (
                                b'080708',
                                b'080708 Records and Information Management (excl. Business Records and Information Management)',
                            ),
                            (
                                b'080709',
                                b'080709 Social and Community Informatics',
                            ),
                            (
                                b'080799',
                                b'080799 Library and Information Studies not elsewhere classified',
                            ),
                            (
                                b'0899',
                                b'0899 OTHER INFORMATION AND COMPUTING SCIENCES',
                            ),
                            (
                                b'089999',
                                b'089999 Information and Computing Sciences not elsewhere classified',
                            ),
                            (b'09', b'09 ENGINEERING'),
                            (b'0901', b'0901 AEROSPACE ENGINEERING'),
                            (
                                b'090101',
                                b'090101 Aerodynamics (excl. Hypersonic Aerodynamics)',
                            ),
                            (b'090102', b'090102 Aerospace Materials'),
                            (b'090103', b'090103 Aerospace Structures'),
                            (
                                b'090104',
                                b'090104 Aircraft Performance and Flight Control Systems',
                            ),
                            (b'090105', b'090105 Avionics'),
                            (b'090106', b'090106 Flight Dynamics'),
                            (
                                b'090107',
                                b'090107 Hypersonic Propulsion and Hypersonic Aerodynamics',
                            ),
                            (
                                b'090108',
                                b'090108 Satellite, Space Vehicle and Missile Design and Testing',
                            ),
                            (
                                b'090199',
                                b'090199 Aerospace Engineering not elsewhere classified',
                            ),
                            (b'0902', b'0902 AUTOMOTIVE ENGINEERING'),
                            (
                                b'090201',
                                b'090201 Automotive Combustion and Fuel Engineering (incl. Alternative/Renewable Fuels)',
                            ),
                            (
                                b'090202',
                                b'090202 Automotive Engineering Materials',
                            ),
                            (b'090203', b'090203 Automotive Mechatronics'),
                            (
                                b'090204',
                                b'090204 Automotive Safety Engineering',
                            ),
                            (
                                b'090205',
                                b'090205 Hybrid Vehicles and Powertrains',
                            ),
                            (
                                b'090299',
                                b'090299 Automotive Engineering not elsewhere classified',
                            ),
                            (b'0903', b'0903 BIOMEDICAL ENGINEERING'),
                            (b'090301', b'090301 Biomaterials'),
                            (b'090302', b'090302 Biomechanical Engineering'),
                            (b'090303', b'090303 Biomedical Instrumentation'),
                            (b'090304', b'090304 Medical Devices'),
                            (b'090305', b'090305 Rehabilitation Engineering'),
                            (
                                b'090399',
                                b'090399 Biomedical Engineering not elsewhere classified',
                            ),
                            (b'0904', b'0904 CHEMICAL ENGINEERING'),
                            (
                                b'090401',
                                b'090401 Carbon Capture Engineering (excl. Sequestration)',
                            ),
                            (
                                b'090402',
                                b'090402 Catalytic Process Engineering',
                            ),
                            (b'090403', b'090403 Chemical Engineering Design'),
                            (
                                b'090404',
                                b'090404 Membrane and Separation Technologies',
                            ),
                            (
                                b'090405',
                                b'090405 Non-automotive Combustion and Fuel Engineering (incl. Alternative/Renewable Fuels)',
                            ),
                            (
                                b'090406',
                                b'090406 Powder and Particle Technology',
                            ),
                            (
                                b'090407',
                                b'090407 Process Control and Simulation',
                            ),
                            (b'090408', b'090408 Rheology'),
                            (
                                b'090409',
                                b'090409 Wastewater Treatment Processes',
                            ),
                            (b'090410', b'090410 Water Treatment Processes'),
                            (
                                b'090499',
                                b'090499 Chemical Engineering not elsewhere classified',
                            ),
                            (b'0905', b'0905 CIVIL ENGINEERING'),
                            (
                                b'090501',
                                b'090501 Civil Geotechnical Engineering',
                            ),
                            (b'090502', b'090502 Construction Engineering'),
                            (b'090503', b'090503 Construction Materials'),
                            (b'090504', b'090504 Earthquake Engineering'),
                            (
                                b'090505',
                                b'090505 Infrastructure Engineering and Asset Management',
                            ),
                            (b'090506', b'090506 Structural Engineering'),
                            (b'090507', b'090507 Transport Engineering'),
                            (b'090508', b'090508 Water Quality Engineering'),
                            (b'090509', b'090509 Water Resources Engineering'),
                            (
                                b'090599',
                                b'090599 Civil Engineering not elsewhere classified',
                            ),
                            (
                                b'0906',
                                b'0906 ELECTRICAL AND ELECTRONIC ENGINEERING',
                            ),
                            (b'090601', b'090601 Circuits and Systems'),
                            (
                                b'090602',
                                b'090602 Control Systems, Robotics and Automation',
                            ),
                            (b'090603', b'090603 Industrial Electronics'),
                            (
                                b'090604',
                                b'090604 Microelectronics and Integrated Circuits',
                            ),
                            (
                                b'090605',
                                b'090605 Photodetectors, Optical Sensors and Solar Cells',
                            ),
                            (
                                b'090606',
                                b'090606 Photonics and Electro-Optical Engineering (excl. Communications)',
                            ),
                            (
                                b'090607',
                                b'090607 Power and Energy Systems Engineering (excl. Renewable Power)',
                            ),
                            (
                                b'090608',
                                b'090608 Renewable Power and Energy Systems Engineering (excl. Solar Cells)',
                            ),
                            (b'090609', b'090609 Signal Processing'),
                            (
                                b'090699',
                                b'090699 Electrical and Electronic Engineering not elsewhere classified',
                            ),
                            (b'0907', b'0907 ENVIRONMENTAL ENGINEERING'),
                            (
                                b'090701',
                                b'090701 Environmental Engineering Design',
                            ),
                            (
                                b'090702',
                                b'090702 Environmental Engineering Modelling',
                            ),
                            (b'090703', b'090703 Environmental Technologies'),
                            (
                                b'090799',
                                b'090799 Environmental Engineering not elsewhere classified',
                            ),
                            (b'0908', b'0908 FOOD SCIENCES'),
                            (
                                b'090801',
                                b'090801 Food Chemistry and Molecular Gastronomy (excl. Wine)',
                            ),
                            (b'090802', b'090802 Food Engineering'),
                            (b'090803', b'090803 Food Nutritional Balance'),
                            (
                                b'090804',
                                b'090804 Food Packaging, Preservation and Safety',
                            ),
                            (b'090805', b'090805 Food Processing'),
                            (
                                b'090806',
                                b'090806 Wine Chemistry and Wine Sensory Science',
                            ),
                            (
                                b'090899',
                                b'090899 Food Sciences not elsewhere classified',
                            ),
                            (b'0909', b'0909 GEOMATIC ENGINEERING'),
                            (b'090901', b'090901 Cartography'),
                            (b'090902', b'090902 Geodesy'),
                            (
                                b'090903',
                                b'090903 Geospatial Information Systems',
                            ),
                            (
                                b'090904',
                                b'090904 Navigation and Position Fixing',
                            ),
                            (
                                b'090905',
                                b'090905 Photogrammetry and Remote Sensing',
                            ),
                            (
                                b'090906',
                                b'090906 Surveying (incl. Hydrographic Surveying)',
                            ),
                            (
                                b'090999',
                                b'090999 Geomatic Engineering not elsewhere classified',
                            ),
                            (b'0910', b'0910 MANUFACTURING ENGINEERING'),
                            (b'091001', b'091001 CAD/CAM Systems'),
                            (
                                b'091002',
                                b'091002 Flexible Manufacturing Systems',
                            ),
                            (b'091003', b'091003 Machine Tools'),
                            (b'091004', b'091004 Machining'),
                            (b'091005', b'091005 Manufacturing Management'),
                            (
                                b'091006',
                                b'091006 Manufacturing Processes and Technologies (excl. Textiles)',
                            ),
                            (
                                b'091007',
                                b'091007 Manufacturing Robotics and Mechatronics (excl. Automotive Mechatronics)',
                            ),
                            (
                                b'091008',
                                b'091008 Manufacturing Safety and Quality',
                            ),
                            (b'091009', b'091009 Microtechnology'),
                            (
                                b'091010',
                                b'091010 Packaging, Storage and Transportation (excl. Food and Agricultural Products)',
                            ),
                            (b'091011', b'091011 Precision Engineering'),
                            (b'091012', b'091012 Textile Technology'),
                            (
                                b'091099',
                                b'091099 Manufacturing Engineering not elsewhere classified',
                            ),
                            (b'0911', b'0911 MARITIME ENGINEERING'),
                            (b'091101', b'091101 Marine Engineering'),
                            (b'091102', b'091102 Naval Architecture'),
                            (b'091103', b'091103 Ocean Engineering'),
                            (
                                b'091104',
                                b'091104 Ship and Platform Hydrodynamics',
                            ),
                            (
                                b'091105',
                                b'091105 Ship and Platform Structures',
                            ),
                            (b'091106', b'091106 Special Vehicles'),
                            (
                                b'091199',
                                b'091199 Maritime Engineering not elsewhere classified',
                            ),
                            (b'0912', b'0912 MATERIALS ENGINEERING'),
                            (b'091201', b'091201 Ceramics'),
                            (
                                b'091202',
                                b'091202 Composite and Hybrid Materials',
                            ),
                            (b'091203', b'091203 Compound Semiconductors'),
                            (b'091204', b'091204 Elemental Semiconductors'),
                            (b'091205', b'091205 Functional Materials'),
                            (b'091206', b'091206 Glass'),
                            (b'091207', b'091207 Metals and Alloy Materials'),
                            (b'091208', b'091208 Organic Semiconductors'),
                            (b'091209', b'091209 Polymers and Plastics'),
                            (b'091210', b'091210 Timber, Pulp and Paper'),
                            (
                                b'091299',
                                b'091299 Materials Engineering not elsewhere classified',
                            ),
                            (b'0913', b'0913 MECHANICAL ENGINEERING'),
                            (
                                b'091301',
                                b'091301 Acoustics and Noise Control (excl. Architectural Acoustics)',
                            ),
                            (
                                b'091302',
                                b'091302 Automation and Control Engineering',
                            ),
                            (b'091303', b'091303 Autonomous Vehicles'),
                            (
                                b'091304',
                                b'091304 Dynamics, Vibration and Vibration Control',
                            ),
                            (
                                b'091305',
                                b'091305 Energy Generation, Conversion and Storage Engineering',
                            ),
                            (
                                b'091306',
                                b'091306 Microelectromechanical Systems (MEMS)',
                            ),
                            (
                                b'091307',
                                b'091307 Numerical Modelling and Mechanical Characterisation',
                            ),
                            (b'091308', b'091308 Solid Mechanics'),
                            (b'091309', b'091309 Tribology'),
                            (
                                b'091399',
                                b'091399 Mechanical Engineering not elsewhere classified',
                            ),
                            (
                                b'0914',
                                b'0914 RESOURCES ENGINEERING AND EXTRACTIVE METALLURGY',
                            ),
                            (b'091401', b'091401 Electrometallurgy'),
                            (
                                b'091402',
                                b'091402 Geomechanics and Resources Geotechnical Engineering',
                            ),
                            (b'091403', b'091403 Hydrometallurgy'),
                            (
                                b'091404',
                                b'091404 Mineral Processing/Beneficiation',
                            ),
                            (b'091405', b'091405 Mining Engineering'),
                            (
                                b'091406',
                                b'091406 Petroleum and Reservoir Engineering',
                            ),
                            (b'091407', b'091407 Pyrometallurgy'),
                            (
                                b'091499',
                                b'091499 Resources Engineering and Extractive Metallurgy not elsewhere classified',
                            ),
                            (b'0915', b'0915 INTERDISCIPLINARY ENGINEERING'),
                            (
                                b'091501',
                                b'091501 Computational Fluid Dynamics',
                            ),
                            (b'091502', b'091502 Computational Heat Transfer'),
                            (b'091503', b'091503 Engineering Practice'),
                            (
                                b'091504',
                                b'091504 Fluidisation and Fluid Mechanics',
                            ),
                            (
                                b'091505',
                                b'091505 Heat and Mass Transfer Operations',
                            ),
                            (
                                b'091506',
                                b'091506 Nuclear Engineering (incl. Fuel Enrichment and Waste Processing and Storage)',
                            ),
                            (
                                b'091507',
                                b'091507 Risk Engineering (excl. Earthquake Engineering)',
                            ),
                            (b'091508', b'091508 Turbulent Flows'),
                            (
                                b'091599',
                                b'091599 Interdisciplinary Engineering not elsewhere classified',
                            ),
                            (b'0999', b'0999 OTHER ENGINEERING'),
                            (b'099901', b'099901 Agricultural Engineering'),
                            (b'099902', b'099902 Engineering Instrumentation'),
                            (
                                b'099999',
                                b'099999 Engineering not elsewhere classified',
                            ),
                            (b'10', b'10 TECHNOLOGY'),
                            (b'1001', b'1001 AGRICULTURAL BIOTECHNOLOGY'),
                            (
                                b'100101',
                                b'100101 Agricultural Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100102',
                                b'100102 Agricultural Marine Biotechnology',
                            ),
                            (
                                b'100103',
                                b'100103 Agricultural Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100104',
                                b'100104 Genetically Modified Animals',
                            ),
                            (
                                b'100105',
                                b'100105 Genetically Modified Field Crops and Pasture',
                            ),
                            (
                                b'100106',
                                b'100106 Genetically Modified Horticulture Plants',
                            ),
                            (b'100107', b'100107 Genetically Modified Trees'),
                            (b'100108', b'100108 Livestock Cloning'),
                            (b'100109', b'100109 Transgenesis'),
                            (
                                b'100199',
                                b'100199 Agricultural Biotechnology not elsewhere classified',
                            ),
                            (b'1002', b'1002 ENVIRONMENTAL BIOTECHNOLOGY'),
                            (b'100201', b'100201 Biodiscovery'),
                            (b'100202', b'100202 Biological Control'),
                            (b'100203', b'100203 Bioremediation'),
                            (
                                b'100204',
                                b'100204 Environmental Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100205',
                                b'100205 Environmental Marine Biotechnology',
                            ),
                            (
                                b'100206',
                                b'100206 Environmental Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100299',
                                b'100299 Environmental Biotechnology not elsewhere classified',
                            ),
                            (b'1003', b'1003 INDUSTRIAL BIOTECHNOLOGY'),
                            (
                                b'100301',
                                b'100301 Biocatalysis and Enzyme Technology',
                            ),
                            (
                                b'100302',
                                b'100302 Bioprocessing, Bioproduction and Bioproducts',
                            ),
                            (b'100303', b'100303 Fermentation'),
                            (
                                b'100304',
                                b'100304 Industrial Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100305',
                                b'100305 Industrial Microbiology (incl. Biofeedstocks)',
                            ),
                            (
                                b'100306',
                                b'100306 Industrial Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100399',
                                b'100399 Industrial Biotechnology not elsewhere classified',
                            ),
                            (b'1004', b'1004 MEDICAL BIOTECHNOLOGY'),
                            (b'100401', b'100401 Gene and Molecular Therapy'),
                            (
                                b'100402',
                                b'100402 Medical Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100403',
                                b'100403 Medical Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100404',
                                b'100404 Regenerative Medicine (incl. Stem Cells and Tissue Engineering)',
                            ),
                            (
                                b'100499',
                                b'100499 Medical Biotechnology not elsewhere classified',
                            ),
                            (b'1005', b'1005 COMMUNICATIONS TECHNOLOGIES'),
                            (b'100501', b'100501 Antennas and Propagation'),
                            (
                                b'100502',
                                b'100502 Broadband and Modem Technology',
                            ),
                            (
                                b'100503',
                                b'100503 Computer Communications Networks',
                            ),
                            (b'100504', b'100504 Data Communications'),
                            (
                                b'100505',
                                b'100505 Microwave and Millimetrewave Theory and Technology',
                            ),
                            (
                                b'100506',
                                b'100506 Optical Fibre Communications',
                            ),
                            (
                                b'100507',
                                b'100507 Optical Networks and Systems',
                            ),
                            (b'100508', b'100508 Satellite Communications'),
                            (b'100509', b'100509 Video Communications'),
                            (b'100510', b'100510 Wireless Communications'),
                            (
                                b'100599',
                                b'100599 Communications Technologies not elsewhere classified',
                            ),
                            (b'1006', b'1006 COMPUTER HARDWARE'),
                            (
                                b'100601',
                                b'100601 Arithmetic and Logic Structures',
                            ),
                            (
                                b'100602',
                                b'100602 Input, Output and Data Devices',
                            ),
                            (b'100603', b'100603 Logic Design'),
                            (b'100604', b'100604 Memory Structures'),
                            (
                                b'100605',
                                b'100605 Performance Evaluation; Testing and Simulation of Reliability',
                            ),
                            (b'100606', b'100606 Processor Architectures'),
                            (
                                b'100699',
                                b'100699 Computer Hardware not elsewhere classified',
                            ),
                            (b'1007', b'1007 NANOTECHNOLOGY'),
                            (
                                b'100701',
                                b'100701 Environmental Nanotechnology',
                            ),
                            (
                                b'100702',
                                b'100702 Molecular and Organic Electronics',
                            ),
                            (b'100703', b'100703 Nanobiotechnology'),
                            (
                                b'100704',
                                b'100704 Nanoelectromechanical Systems',
                            ),
                            (b'100705', b'100705 Nanoelectronics'),
                            (
                                b'100706',
                                b'100706 Nanofabrication, Growth and Self Assembly',
                            ),
                            (b'100707', b'100707 Nanomanufacturing'),
                            (b'100708', b'100708 Nanomaterials'),
                            (b'100709', b'100709 Nanomedicine'),
                            (b'100710', b'100710 Nanometrology'),
                            (b'100711', b'100711 Nanophotonics'),
                            (b'100712', b'100712 Nanoscale Characterisation'),
                            (
                                b'100713',
                                b'100713 Nanotoxicology, Health and Safety',
                            ),
                            (
                                b'100799',
                                b'100799 Nanotechnology not elsewhere classified',
                            ),
                            (b'1099', b'1099 OTHER TECHNOLOGY'),
                            (
                                b'109999',
                                b'109999 Technology not elsewhere classified',
                            ),
                            (b'11', b'11 MEDICAL AND HEALTH SCIENCES'),
                            (
                                b'1101',
                                b'1101 MEDICAL BIOCHEMISTRY AND METABOLOMICS',
                            ),
                            (
                                b'110101',
                                b'110101 Medical Biochemistry: Amino Acids and Metabolites',
                            ),
                            (
                                b'110102',
                                b'110102 Medical Biochemistry: Carbohydrates',
                            ),
                            (
                                b'110103',
                                b'110103 Medical Biochemistry: Inorganic Elements and Compounds',
                            ),
                            (
                                b'110104',
                                b'110104 Medical Biochemistry: Lipids',
                            ),
                            (
                                b'110105',
                                b'110105 Medical Biochemistry: Nucleic Acids',
                            ),
                            (
                                b'110106',
                                b'110106 Medical Biochemistry: Proteins and Peptides (incl. Medical Proteomics)',
                            ),
                            (b'110107', b'110107 Metabolic Medicine'),
                            (
                                b'110199',
                                b'110199 Medical Biochemistry and Metabolomics not elsewhere classified',
                            ),
                            (
                                b'1102',
                                b'1102 CARDIORESPIRATORY MEDICINE AND HAEMATOLOGY',
                            ),
                            (
                                b'110201',
                                b'110201 Cardiology (incl. Cardiovascular Diseases)',
                            ),
                            (b'110202', b'110202 Haematology'),
                            (b'110203', b'110203 Respiratory Diseases'),
                            (
                                b'110299',
                                b'110299 Cardiorespiratory Medicine and Haematology not elsewhere classified',
                            ),
                            (b'1103', b'1103 CLINICAL SCIENCES'),
                            (b'110301', b'110301 Anaesthesiology'),
                            (
                                b'110302',
                                b'110302 Clinical Chemistry (diagnostics)',
                            ),
                            (b'110303', b'110303 Clinical Microbiology'),
                            (b'110304', b'110304 Dermatology'),
                            (b'110305', b'110305 Emergency Medicine'),
                            (b'110306', b'110306 Endocrinology'),
                            (
                                b'110307',
                                b'110307 Gastroenterology and Hepatology',
                            ),
                            (b'110308', b'110308 Geriatrics and Gerontology'),
                            (b'110309', b'110309 Infectious Diseases'),
                            (b'110310', b'110310 Intensive Care'),
                            (
                                b'110311',
                                b'110311 Medical Genetics (excl. Cancer Genetics)',
                            ),
                            (b'110312', b'110312 Nephrology and Urology'),
                            (b'110313', b'110313 Nuclear Medicine'),
                            (b'110314', b'110314 Orthopaedics'),
                            (b'110315', b'110315 Otorhinolaryngology'),
                            (
                                b'110316',
                                b'110316 Pathology (excl. Oral Pathology)',
                            ),
                            (b'110317', b'110317 Physiotherapy'),
                            (b'110318', b'110318 Podiatry'),
                            (
                                b'110319',
                                b'110319 Psychiatry (incl. Psychotherapy)',
                            ),
                            (b'110320', b'110320 Radiology and Organ Imaging'),
                            (
                                b'110321',
                                b'110321 Rehabilitation and Therapy (excl. Physiotherapy)',
                            ),
                            (b'110322', b'110322 Rheumatology and Arthritis'),
                            (b'110323', b'110323 Surgery'),
                            (b'110324', b'110324 Venereology'),
                            (
                                b'110399',
                                b'110399 Clinical Sciences not elsewhere classified',
                            ),
                            (
                                b'1104',
                                b'1104 COMPLEMENTARY AND ALTERNATIVE MEDICINE',
                            ),
                            (b'110401', b'110401 Chiropractic'),
                            (b'110402', b'110402 Naturopathy'),
                            (
                                b'110403',
                                b'110403 Traditional Aboriginal and Torres Strait Islander Medicine and Treatments',
                            ),
                            (
                                b'110404',
                                b'110404 Traditional Chinese Medicine and Treatments',
                            ),
                            (
                                b'110405',
                                b'110405 Traditional Maori Medicine and Treatments',
                            ),
                            (
                                b'110499',
                                b'110499 Complementary and Alternative Medicine not elsewhere classified',
                            ),
                            (b'1105', b'1105 DENTISTRY'),
                            (
                                b'110501',
                                b'110501 Dental Materials and Equipment',
                            ),
                            (
                                b'110502',
                                b'110502 Dental Therapeutics, Pharmacology and Toxicology',
                            ),
                            (b'110503', b'110503 Endodontics'),
                            (
                                b'110504',
                                b'110504 Oral and Maxillofacial Surgery',
                            ),
                            (b'110505', b'110505 Oral Medicine and Pathology'),
                            (
                                b'110506',
                                b'110506 Orthodontics and Dentofacial Orthopaedics',
                            ),
                            (b'110507', b'110507 Paedodontics'),
                            (b'110508', b'110508 Periodontics'),
                            (b'110509', b'110509 Special Needs Dentistry'),
                            (
                                b'110599',
                                b'110599 Dentistry not elsewhere classified',
                            ),
                            (
                                b'1106',
                                b'1106 HUMAN MOVEMENT AND SPORTS SCIENCE',
                            ),
                            (b'110601', b'110601 Biomechanics'),
                            (b'110602', b'110602 Exercise Physiology'),
                            (b'110603', b'110603 Motor Control'),
                            (b'110604', b'110604 Sports Medicine'),
                            (
                                b'110699',
                                b'110699 Human Movement and Sports Science not elsewhere classified',
                            ),
                            (b'1107', b'1107 IMMUNOLOGY'),
                            (b'110701', b'110701 Allergy'),
                            (
                                b'110702',
                                b'110702 Applied Immunology (incl. Antibody Engineering, Xenotransplantation and T-cell Therapies)',
                            ),
                            (b'110703', b'110703 Autoimmunity'),
                            (b'110704', b'110704 Cellular Immunology'),
                            (
                                b'110705',
                                b'110705 Humoural Immunology and Immunochemistry',
                            ),
                            (
                                b'110706',
                                b'110706 Immunogenetics (incl. Genetic Immunology)',
                            ),
                            (b'110707', b'110707 Innate Immunity'),
                            (b'110708', b'110708 Transplantation Immunology'),
                            (b'110709', b'110709 Tumour Immunology'),
                            (
                                b'110799',
                                b'110799 Immunology not elsewhere classified',
                            ),
                            (b'1108', b'1108 MEDICAL MICROBIOLOGY'),
                            (b'110801', b'110801 Medical Bacteriology'),
                            (
                                b'110802',
                                b'110802 Medical Infection Agents (incl. Prions)',
                            ),
                            (b'110803', b'110803 Medical Parasitology'),
                            (b'110804', b'110804 Medical Virology'),
                            (
                                b'110899',
                                b'110899 Medical Microbiology not elsewhere classified',
                            ),
                            (b'1109', b'1109 NEUROSCIENCES'),
                            (b'110901', b'110901 Autonomic Nervous System'),
                            (b'110902', b'110902 Cellular Nervous System'),
                            (b'110903', b'110903 Central Nervous System'),
                            (
                                b'110904',
                                b'110904 Neurology and Neuromuscular Diseases',
                            ),
                            (b'110905', b'110905 Peripheral Nervous System'),
                            (b'110906', b'110906 Sensory Systems'),
                            (
                                b'110999',
                                b'110999 Neurosciences not elsewhere classified',
                            ),
                            (b'1110', b'1110 NURSING'),
                            (b'111001', b'111001 Aged Care Nursing'),
                            (
                                b'111002',
                                b'111002 Clinical Nursing: Primary (Preventative)',
                            ),
                            (
                                b'111003',
                                b'111003 Clinical Nursing: Secondary (Acute Care)',
                            ),
                            (
                                b'111004',
                                b'111004 Clinical Nursing: Tertiary (Rehabilitative)',
                            ),
                            (b'111005', b'111005 Mental Health Nursing'),
                            (b'111006', b'111006 Midwifery'),
                            (
                                b'111099',
                                b'111099 Nursing not elsewhere classified',
                            ),
                            (b'1111', b'1111 NUTRITION AND DIETETICS'),
                            (
                                b'111101',
                                b'111101 Clinical and Sports Nutrition',
                            ),
                            (b'111102', b'111102 Dietetics and Nutrigenomics'),
                            (b'111103', b'111103 Nutritional Physiology'),
                            (
                                b'111104',
                                b'111104 Public Nutrition Intervention',
                            ),
                            (
                                b'111199',
                                b'111199 Nutrition and Dietetics not elsewhere classified',
                            ),
                            (b'1112', b'1112 ONCOLOGY AND CARCINOGENESIS'),
                            (b'111201', b'111201 Cancer Cell Biology'),
                            (b'111202', b'111202 Cancer Diagnosis'),
                            (b'111203', b'111203 Cancer Genetics'),
                            (
                                b'111204',
                                b'111204 Cancer Therapy (excl. Chemotherapy and Radiation Therapy)',
                            ),
                            (b'111205', b'111205 Chemotherapy'),
                            (b'111206', b'111206 Haematological Tumours'),
                            (b'111207', b'111207 Molecular Targets'),
                            (b'111208', b'111208 Radiation Therapy'),
                            (b'111209', b'111209 Solid Tumours'),
                            (
                                b'111299',
                                b'111299 Oncology and Carcinogenesis not elsewhere classified',
                            ),
                            (b'1113', b'1113 OPHTHALMOLOGY AND OPTOMETRY'),
                            (b'111301', b'111301 Ophthalmology'),
                            (b'111302', b'111302 Optical Technology'),
                            (b'111303', b'111303 Vision Science'),
                            (
                                b'111399',
                                b'111399 Ophthalmology and Optometry not elsewhere classified',
                            ),
                            (
                                b'1114',
                                b'1114 PAEDIATRICS AND REPRODUCTIVE MEDICINE',
                            ),
                            (
                                b'111401',
                                b'111401 Foetal Development and Medicine',
                            ),
                            (b'111402', b'111402 Obstetrics and Gynaecology'),
                            (b'111403', b'111403 Paediatrics'),
                            (b'111404', b'111404 Reproduction'),
                            (
                                b'111499',
                                b'111499 Paediatrics and Reproductive Medicine not elsewhere classified',
                            ),
                            (
                                b'1115',
                                b'1115 PHARMACOLOGY AND PHARMACEUTICAL SCIENCES',
                            ),
                            (b'111501', b'111501 Basic Pharmacology'),
                            (
                                b'111502',
                                b'111502 Clinical Pharmacology and Therapeutics',
                            ),
                            (
                                b'111503',
                                b'111503 Clinical Pharmacy and Pharmacy Practice',
                            ),
                            (b'111504', b'111504 Pharmaceutical Sciences'),
                            (b'111505', b'111505 Pharmacogenomics'),
                            (
                                b'111506',
                                b'111506 Toxicology (incl. Clinical Toxicology)',
                            ),
                            (
                                b'111599',
                                b'111599 Pharmacology and Pharmaceutical Sciences not elsewhere classified',
                            ),
                            (b'1116', b'1116 MEDICAL PHYSIOLOGY'),
                            (b'111601', b'111601 Cell Physiology'),
                            (b'111602', b'111602 Human Biophysics'),
                            (b'111603', b'111603 Systems Physiology'),
                            (
                                b'111699',
                                b'111699 Medical Physiology not elsewhere classified',
                            ),
                            (
                                b'1117',
                                b'1117 PUBLIC HEALTH AND HEALTH SERVICES',
                            ),
                            (
                                b'111701',
                                b'111701 Aboriginal and Torres Strait Islander Health',
                            ),
                            (b'111702', b'111702 Aged Health Care'),
                            (b'111703', b'111703 Care for Disabled'),
                            (b'111704', b'111704 Community Child Health'),
                            (
                                b'111705',
                                b'111705 Environmental and Occupational Health and Safety',
                            ),
                            (b'111706', b'111706 Epidemiology'),
                            (b'111707', b'111707 Family Care'),
                            (
                                b'111708',
                                b'111708 Health and Community Services',
                            ),
                            (b'111709', b'111709 Health Care Administration'),
                            (b'111710', b'111710 Health Counselling'),
                            (
                                b'111711',
                                b'111711 Health Information Systems (incl. Surveillance)',
                            ),
                            (b'111712', b'111712 Health Promotion'),
                            (b'111713', b'111713 Maori Health'),
                            (b'111714', b'111714 Mental Health'),
                            (b'111715', b'111715 Pacific Peoples Health'),
                            (b'111716', b'111716 Preventive Medicine'),
                            (b'111717', b'111717 Primary Health Care'),
                            (b'111718', b'111718 Residential Client Care'),
                            (
                                b'111799',
                                b'111799 Public Health and Health Services not elsewhere classified',
                            ),
                            (
                                b'1199',
                                b'1199 OTHER MEDICAL AND HEALTH SCIENCES',
                            ),
                            (
                                b'119999',
                                b'119999 Medical and Health Sciences not elsewhere classified',
                            ),
                            (b'12', b'12 BUILT ENVIRONMENT AND DESIGN'),
                            (b'1201', b'1201 ARCHITECTURE'),
                            (b'120101', b'120101 Architectural Design'),
                            (
                                b'120102',
                                b'120102 Architectural Heritage and Conservation',
                            ),
                            (
                                b'120103',
                                b'120103 Architectural History and Theory',
                            ),
                            (
                                b'120104',
                                b'120104 Architectural Science and Technology (incl. Acoustics, Lighting, Structure and Ecologically Sustainable Design)',
                            ),
                            (b'120105', b'120105 Architecture Management'),
                            (b'120106', b'120106 Interior Design'),
                            (b'120107', b'120107 Landscape Architecture'),
                            (
                                b'120199',
                                b'120199 Architecture not elsewhere classified',
                            ),
                            (b'1202', b'1202 BUILDING'),
                            (
                                b'120201',
                                b'120201 Building Construction Management and Project Planning',
                            ),
                            (
                                b'120202',
                                b'120202 Building Science and Techniques',
                            ),
                            (b'120203', b'120203 Quantity Surveying'),
                            (
                                b'120299',
                                b'120299 Building not elsewhere classified',
                            ),
                            (b'1203', b'1203 DESIGN PRACTICE AND MANAGEMENT'),
                            (b'120301', b'120301 Design History and Theory'),
                            (b'120302', b'120302 Design Innovation'),
                            (
                                b'120303',
                                b'120303 Design Management and Studio and Professional Practice',
                            ),
                            (
                                b'120304',
                                b'120304 Digital and Interaction Design',
                            ),
                            (b'120305', b'120305 Industrial Design'),
                            (b'120306', b'120306 Textile and Fashion Design'),
                            (
                                b'120307',
                                b'120307 Visual Communication Design (incl. Graphic Design)',
                            ),
                            (
                                b'120399',
                                b'120399 Design Practice and Management not elsewhere classified',
                            ),
                            (b'1204', b'1204 ENGINEERING DESIGN'),
                            (
                                b'120401',
                                b'120401 Engineering Design Empirical Studies',
                            ),
                            (
                                b'120402',
                                b'120402 Engineering Design Knowledge',
                            ),
                            (b'120403', b'120403 Engineering Design Methods'),
                            (b'120404', b'120404 Engineering Systems Design'),
                            (
                                b'120405',
                                b'120405 Models of Engineering Design',
                            ),
                            (
                                b'120499',
                                b'120499 Engineering Design not elsewhere classified',
                            ),
                            (b'1205', b'1205 URBAN AND REGIONAL PLANNING'),
                            (b'120501', b'120501 Community Planning'),
                            (
                                b'120502',
                                b'120502 History and Theory of the Built Environment (excl. Architecture)',
                            ),
                            (
                                b'120503',
                                b'120503 Housing Markets, Development, Management',
                            ),
                            (
                                b'120504',
                                b'120504 Land Use and Environmental Planning',
                            ),
                            (
                                b'120505',
                                b'120505 Regional Analysis and Development',
                            ),
                            (b'120506', b'120506 Transport Planning'),
                            (
                                b'120507',
                                b'120507 Urban Analysis and Development',
                            ),
                            (b'120508', b'120508 Urban Design'),
                            (
                                b'120599',
                                b'120599 Urban and Regional Planning not elsewhere classified',
                            ),
                            (
                                b'1299',
                                b'1299 OTHER BUILT ENVIRONMENT AND DESIGN',
                            ),
                            (
                                b'129999',
                                b'129999 Built Environment and Design not elsewhere classified',
                            ),
                            (b'13', b'13 EDUCATION'),
                            (b'1301', b'1301 EDUCATION SYSTEMS'),
                            (
                                b'130101',
                                b'130101 Continuing and Community Education',
                            ),
                            (
                                b'130102',
                                b'130102 Early Childhood Education (excl. Maori)',
                            ),
                            (b'130103', b'130103 Higher Education'),
                            (
                                b'130104',
                                b'130104 Kura Kaupapa Maori (Maori Primary Education)',
                            ),
                            (
                                b'130105',
                                b'130105 Primary Education (excl. Maori)',
                            ),
                            (b'130106', b'130106 Secondary Education'),
                            (
                                b'130107',
                                b'130107 Te Whariki (Maori Early Childhood Education)',
                            ),
                            (
                                b'130108',
                                b'130108 Technical, Further and Workplace Education',
                            ),
                            (
                                b'130199',
                                b'130199 Education systems not elsewhere classified',
                            ),
                            (b'1302', b'1302 CURRICULUM AND PEDAGOGY'),
                            (
                                b'130201',
                                b'130201 Creative Arts, Media and Communication Curriculum and Pedagogy',
                            ),
                            (
                                b'130202',
                                b'130202 Curriculum and Pedagogy Theory and Development',
                            ),
                            (
                                b'130203',
                                b'130203 Economics, Business and Management Curriculum and Pedagogy',
                            ),
                            (
                                b'130204',
                                b'130204 English and Literacy Curriculum and Pedagogy (excl. LOTE, ESL and TESOL)',
                            ),
                            (
                                b'130205',
                                b'130205 Humanities and Social Sciences Curriculum and Pedagogy (excl. Economics, Business and Management)',
                            ),
                            (
                                b'130206',
                                b'130206 Kohanga Reo (Maori Language Curriculum and Pedagogy)',
                            ),
                            (
                                b'130207',
                                b'130207 LOTE, ESL and TESOL Curriculum and Pedagogy (excl. Maori)',
                            ),
                            (
                                b'130208',
                                b'130208 Mathematics and Numeracy Curriculum and Pedagogy',
                            ),
                            (
                                b'130209',
                                b'130209 Medicine, Nursing and Health Curriculum and Pedagogy',
                            ),
                            (
                                b'130210',
                                b'130210 Physical Education and Development Curriculum and Pedagogy',
                            ),
                            (
                                b'130211',
                                b'130211 Religion Curriculum and Pedagogy',
                            ),
                            (
                                b'130212',
                                b'130212 Science, Technology and Engineering Curriculum and Pedagogy',
                            ),
                            (
                                b'130213',
                                b'130213 Vocational Education and Training Curriculum and Pedagogy',
                            ),
                            (
                                b'130299',
                                b'130299 Curriculum and Pedagogy not elsewhere classified',
                            ),
                            (b'1303', b'1303 SPECIALIST STUDIES IN EDUCATION'),
                            (
                                b'130301',
                                b'130301 Aboriginal and Torres Strait Islander Education',
                            ),
                            (
                                b'130302',
                                b'130302 Comparative and Cross-Cultural Education',
                            ),
                            (
                                b'130303',
                                b'130303 Education Assessment and Evaluation',
                            ),
                            (
                                b'130304',
                                b'130304 Educational Administration, Management and Leadership',
                            ),
                            (b'130305', b'130305 Educational Counselling'),
                            (
                                b'130306',
                                b'130306 Educational Technology and Computing',
                            ),
                            (
                                b'130307',
                                b'130307 Ethnic Education (excl. Aboriginal and Torres Strait Islander, Maori and Pacific Peoples)',
                            ),
                            (
                                b'130308',
                                b'130308 Gender, Sexuality and Education',
                            ),
                            (b'130309', b'130309 Learning Sciences'),
                            (
                                b'130310',
                                b'130310 Maori Education (excl. Early Childhood and Primary Education)',
                            ),
                            (b'130311', b'130311 Pacific Peoples Education'),
                            (
                                b'130312',
                                b'130312 Special Education and Disability',
                            ),
                            (
                                b'130313',
                                b'130313 Teacher Education and Professional Development of Educators',
                            ),
                            (
                                b'130399',
                                b'130399 Specialist Studies in Education not elsewhere classified',
                            ),
                            (b'1399', b'1399 OTHER EDUCATION'),
                            (
                                b'139999',
                                b'139999 Education not elsewhere classified',
                            ),
                            (b'14', b'14 ECONOMICS'),
                            (b'1401', b'1401 ECONOMIC THEORY'),
                            (b'140101', b'140101 History of Economic Thought'),
                            (b'140102', b'140102 Macroeconomic Theory'),
                            (b'140103', b'140103 Mathematical Economics'),
                            (b'140104', b'140104 Microeconomic Theory'),
                            (
                                b'140199',
                                b'140199 Economic Theory not elsewhere classified',
                            ),
                            (b'1402', b'1402 APPLIED ECONOMICS'),
                            (b'140201', b'140201 Agricultural Economics'),
                            (
                                b'140202',
                                b'140202 Economic Development and Growth',
                            ),
                            (b'140203', b'140203 Economic History'),
                            (b'140204', b'140204 Economics of Education'),
                            (
                                b'140205',
                                b'140205 Environment and Resource Economics',
                            ),
                            (b'140206', b'140206 Experimental Economics'),
                            (b'140207', b'140207 Financial Economics'),
                            (b'140208', b'140208 Health Economics'),
                            (
                                b'140209',
                                b'140209 Industry Economics and Industrial Organisation',
                            ),
                            (
                                b'140210',
                                b'140210 International Economics and International Finance',
                            ),
                            (b'140211', b'140211 Labour Economics'),
                            (
                                b'140212',
                                b'140212 Macroeconomics (incl. Monetary and Fiscal Theory)',
                            ),
                            (
                                b'140213',
                                b'140213 Public Economics- Public Choice',
                            ),
                            (
                                b'140214',
                                b'140214 Public Economics- Publically Provided Goods',
                            ),
                            (
                                b'140215',
                                b'140215 Public Economics- Taxation and Revenue',
                            ),
                            (b'140216', b'140216 Tourism Economics'),
                            (b'140217', b'140217 Transport Economics'),
                            (
                                b'140218',
                                b'140218 Urban and Regional Economics',
                            ),
                            (b'140219', b'140219 Welfare Economics'),
                            (
                                b'140299',
                                b'140299 Applied Economics not elsewhere classified',
                            ),
                            (b'1403', b'1403 ECONOMETRICS'),
                            (b'140301', b'140301 Cross-Sectional Analysis'),
                            (
                                b'140302',
                                b'140302 Econometric and Statistical Methods',
                            ),
                            (
                                b'140303',
                                b'140303 Economic Models and Forecasting',
                            ),
                            (b'140304', b'140304 Panel Data Analysis'),
                            (b'140305', b'140305 Time-Series Analysis'),
                            (
                                b'140399',
                                b'140399 Econometrics not elsewhere classified',
                            ),
                            (b'1499', b'1499 OTHER ECONOMICS'),
                            (
                                b'149901',
                                b'149901 Comparative Economic Systems',
                            ),
                            (b'149902', b'149902 Ecological Economics'),
                            (b'149903', b'149903 Heterodox Economics'),
                            (
                                b'149999',
                                b'149999 Economics not elsewhere classified',
                            ),
                            (
                                b'15',
                                b'15 COMMERCE, MANAGEMENT, TOURISM AND SERVICES',
                            ),
                            (
                                b'1501',
                                b'1501 ACCOUNTING, AUDITING AND ACCOUNTABILITY',
                            ),
                            (
                                b'150101',
                                b'150101 Accounting Theory and Standards',
                            ),
                            (b'150102', b'150102 Auditing and Accountability'),
                            (b'150103', b'150103 Financial Accounting'),
                            (b'150104', b'150104 International Accounting'),
                            (b'150105', b'150105 Management Accounting'),
                            (
                                b'150106',
                                b'150106 Sustainability Accounting and Reporting',
                            ),
                            (b'150107', b'150107 Taxation Accounting'),
                            (
                                b'150199',
                                b'150199 Accounting, Auditing and Accountability not elsewhere classified',
                            ),
                            (b'1502', b'1502 BANKING, FINANCE AND INVESTMENT'),
                            (b'150201', b'150201 Finance'),
                            (b'150202', b'150202 Financial Econometrics'),
                            (
                                b'150203',
                                b'150203 Financial Institutions (incl. Banking)',
                            ),
                            (b'150204', b'150204 Insurance Studies'),
                            (
                                b'150205',
                                b'150205 Investment and Risk Management',
                            ),
                            (
                                b'150299',
                                b'150299 Banking, Finance and Investment not elsewhere classified',
                            ),
                            (b'1503', b'1503 BUSINESS AND MANAGEMENT'),
                            (
                                b'150301',
                                b'150301 Business Information Management (incl. Records, Knowledge and Information Management, and Intelligence)',
                            ),
                            (
                                b'150302',
                                b'150302 Business Information Systems',
                            ),
                            (
                                b'150303',
                                b'150303 Corporate Governance and Stakeholder Engagement',
                            ),
                            (b'150304', b'150304 Entrepreneurship'),
                            (b'150305', b'150305 Human Resources Management'),
                            (b'150306', b'150306 Industrial Relations'),
                            (
                                b'150307',
                                b'150307 Innovation and Technology Management',
                            ),
                            (b'150308', b'150308 International Business'),
                            (
                                b'150309',
                                b'150309 Logistics and Supply Chain Management',
                            ),
                            (
                                b'150310',
                                b'150310 Organisation and Management Theory',
                            ),
                            (b'150311', b'150311 Organisational Behaviour'),
                            (
                                b'150312',
                                b'150312 Organisational Planning and Management',
                            ),
                            (b'150313', b'150313 Quality Management'),
                            (b'150314', b'150314 Small Business Management'),
                            (
                                b'150399',
                                b'150399 Business and Management not elsewhere classified',
                            ),
                            (b'1504', b'1504 COMMERCIAL SERVICES'),
                            (
                                b'150401',
                                b'150401 Food and Hospitality Services',
                            ),
                            (b'150402', b'150402 Hospitality Management'),
                            (
                                b'150403',
                                b'150403 Real Estate and Valuation Services',
                            ),
                            (
                                b'150404',
                                b'150404 Sport and Leisure Management',
                            ),
                            (
                                b'150499',
                                b'150499 Commercial Services not elsewhere classified',
                            ),
                            (b'1505', b'1505 MARKETING'),
                            (
                                b'150501',
                                b'150501 Consumer-Oriented Product or Service Development',
                            ),
                            (b'150502', b'150502 Marketing Communications'),
                            (
                                b'150503',
                                b'150503 Marketing Management (incl. Strategy and Customer Relations)',
                            ),
                            (b'150504', b'150504 Marketing Measurement'),
                            (
                                b'150505',
                                b'150505 Marketing Research Methodology',
                            ),
                            (b'150506', b'150506 Marketing Theory'),
                            (
                                b'150507',
                                b'150507 Pricing (incl. Consumer Value Estimation)',
                            ),
                            (
                                b'150599',
                                b'150599 Marketing not elsewhere classified',
                            ),
                            (b'1506', b'1506 TOURISM'),
                            (b'150601', b'150601 Impacts of Tourism'),
                            (b'150602', b'150602 Tourism Forecasting'),
                            (b'150603', b'150603 Tourism Management'),
                            (b'150604', b'150604 Tourism Marketing'),
                            (b'150605', b'150605 Tourism Resource Appraisal'),
                            (
                                b'150606',
                                b'150606 Tourist Behaviour and Visitor Experience',
                            ),
                            (
                                b'150699',
                                b'150699 Tourism not elsewhere classified',
                            ),
                            (
                                b'1507',
                                b'1507 TRANSPORTATION AND FREIGHT SERVICES',
                            ),
                            (
                                b'150701',
                                b'150701 Air Transportation and Freight Services',
                            ),
                            (
                                b'150702',
                                b'150702 Rail Transportation and Freight Services',
                            ),
                            (
                                b'150703',
                                b'150703 Road Transportation and Freight Services',
                            ),
                            (
                                b'150799',
                                b'150799 Transportation and Freight Services not elsewhere classified',
                            ),
                            (
                                b'1599',
                                b'1599 OTHER COMMERCE, MANAGEMENT, TOURISM AND SERVICES',
                            ),
                            (
                                b'159999',
                                b'159999 Commerce, Management, Tourism and Services not elsewhere classified',
                            ),
                            (b'16', b'16 STUDIES IN HUMAN SOCIETY'),
                            (b'1601', b'1601 ANTHROPOLOGY'),
                            (b'160101', b'160101 Anthropology of Development'),
                            (
                                b'160102',
                                b'160102 Biological (Physical) Anthropology',
                            ),
                            (b'160103', b'160103 Linguistic Anthropology'),
                            (
                                b'160104',
                                b'160104 Social and Cultural Anthropology',
                            ),
                            (
                                b'160199',
                                b'160199 Anthropology not elsewhere classified',
                            ),
                            (b'1602', b'1602 CRIMINOLOGY'),
                            (
                                b'160201',
                                b'160201 Causes and Prevention of Crime',
                            ),
                            (
                                b'160202',
                                b'160202 Correctional Theory, Offender Treatment and Rehabilitation',
                            ),
                            (b'160203', b'160203 Courts and Sentencing'),
                            (b'160204', b'160204 Criminological Theories'),
                            (
                                b'160205',
                                b'160205 Police Administration, Procedures and Practice',
                            ),
                            (
                                b'160206',
                                b'160206 Private Policing and Security Services',
                            ),
                            (
                                b'160299',
                                b'160299 Criminology not elsewhere classified',
                            ),
                            (b'1603', b'1603 DEMOGRAPHY'),
                            (
                                b'160301',
                                b'160301 Family and Household Studies',
                            ),
                            (b'160302', b'160302 Fertility'),
                            (b'160303', b'160303 Migration'),
                            (b'160304', b'160304 Mortality'),
                            (
                                b'160305',
                                b'160305 Population Trends and Policies',
                            ),
                            (
                                b'160399',
                                b'160399 Demography not elsewhere classified',
                            ),
                            (b'1604', b'1604 HUMAN GEOGRAPHY'),
                            (b'160401', b'160401 Economic Geography'),
                            (
                                b'160402',
                                b'160402 Recreation, Leisure and Tourism Geography',
                            ),
                            (
                                b'160403',
                                b'160403 Social and Cultural Geography',
                            ),
                            (
                                b'160404',
                                b'160404 Urban and Regional Studies (excl. Planning)',
                            ),
                            (
                                b'160499',
                                b'160499 Human Geography not elsewhere classified',
                            ),
                            (b'1605', b'1605 POLICY AND ADMINISTRATION'),
                            (
                                b'160501',
                                b'160501 Aboriginal and Torres Strait Islander Policy',
                            ),
                            (b'160502', b'160502 Arts and Cultural Policy'),
                            (
                                b'160503',
                                b'160503 Communications and Media Policy',
                            ),
                            (b'160504', b'160504 Crime Policy'),
                            (b'160505', b'160505 Economic Development Policy'),
                            (b'160506', b'160506 Education Policy'),
                            (b'160507', b'160507 Environment Policy'),
                            (b'160508', b'160508 Health Policy'),
                            (b'160509', b'160509 Public Administration'),
                            (b'160510', b'160510 Public Policy'),
                            (
                                b'160511',
                                b'160511 Research, Science and Technology Policy',
                            ),
                            (b'160512', b'160512 Social Policy'),
                            (b'160513', b'160513 Tourism Policy'),
                            (b'160514', b'160514 Urban Policy'),
                            (
                                b'160599',
                                b'160599 Policy and Administration not elsewhere classified',
                            ),
                            (b'1606', b'1606 POLITICAL SCIENCE'),
                            (
                                b'160601',
                                b'160601 Australian Government and Politics',
                            ),
                            (b'160602', b'160602 Citizenship'),
                            (
                                b'160603',
                                b'160603 Comparative Government and Politics',
                            ),
                            (b'160604', b'160604 Defence Studies'),
                            (b'160605', b'160605 Environmental Politics'),
                            (
                                b'160606',
                                b'160606 Government and Politics of Asia and the Pacific',
                            ),
                            (b'160607', b'160607 International Relations'),
                            (
                                b'160608',
                                b'160608 New Zealand Government and Politics',
                            ),
                            (
                                b'160609',
                                b'160609 Political Theory and Political Philosophy',
                            ),
                            (
                                b'160699',
                                b'160699 Political Science not elsewhere classified',
                            ),
                            (b'1607', b'1607 SOCIAL WORK'),
                            (
                                b'160701',
                                b'160701 Clinical Social Work Practice',
                            ),
                            (
                                b'160702',
                                b'160702 Counselling, Welfare and Community Services',
                            ),
                            (b'160703', b'160703 Social Program Evaluation'),
                            (
                                b'160799',
                                b'160799 Social Work not elsewhere classified',
                            ),
                            (b'1608', b'1608 SOCIOLOGY'),
                            (
                                b'160801',
                                b'160801 Applied Sociology, Program Evaluation and Social Impact Assessment',
                            ),
                            (b'160802', b'160802 Environmental Sociology'),
                            (b'160803', b'160803 Race and Ethnic Relations'),
                            (b'160804', b'160804 Rural Sociology'),
                            (b'160805', b'160805 Social Change'),
                            (b'160806', b'160806 Social Theory'),
                            (
                                b'160807',
                                b'160807 Sociological Methodology and Research Methods',
                            ),
                            (
                                b'160808',
                                b'160808 Sociology and Social Studies of Science and Technology',
                            ),
                            (b'160809', b'160809 Sociology of Education'),
                            (
                                b'160810',
                                b'160810 Urban Sociology and Community Studies',
                            ),
                            (
                                b'160899',
                                b'160899 Sociology not elsewhere classified',
                            ),
                            (b'1699', b'1699 OTHER STUDIES IN HUMAN SOCIETY'),
                            (b'169901', b'169901 Gender Specific Studies'),
                            (
                                b'169902',
                                b'169902 Studies of Aboriginal and Torres Strait Islander Society',
                            ),
                            (b'169903', b'169903 Studies of Asian Society'),
                            (b'169904', b'169904 Studies of Maori Society'),
                            (
                                b'169905',
                                b"169905 Studies of Pacific Peoples' Societies",
                            ),
                            (
                                b'169999',
                                b'169999 Studies in Human Society not elsewhere classified',
                            ),
                            (b'17', b'17 PSYCHOLOGY AND COGNITIVE SCIENCES'),
                            (b'1701', b'1701 PSYCHOLOGY'),
                            (
                                b'170101',
                                b'170101 Biological Psychology (Neuropsychology, Psychopharmacology, Physiological Psychology)',
                            ),
                            (
                                b'170102',
                                b'170102 Developmental Psychology and Ageing',
                            ),
                            (b'170103', b'170103 Educational Psychology'),
                            (b'170104', b'170104 Forensic Psychology'),
                            (b'170105', b'170105 Gender Psychology'),
                            (
                                b'170106',
                                b'170106 Health, Clinical and Counselling Psychology',
                            ),
                            (
                                b'170107',
                                b'170107 Industrial and Organisational Psychology',
                            ),
                            (b'170108', b'170108 Kaupapa Maori Psychology'),
                            (
                                b'170109',
                                b'170109 Personality, Abilities and Assessment',
                            ),
                            (
                                b'170110',
                                b'170110 Psychological Methodology, Design and Analysis',
                            ),
                            (b'170111', b'170111 Psychology of Religion'),
                            (
                                b'170112',
                                b'170112 Sensory Processes, Perception and Performance',
                            ),
                            (
                                b'170113',
                                b'170113 Social and Community Psychology',
                            ),
                            (
                                b'170114',
                                b'170114 Sport and Exercise Psychology',
                            ),
                            (
                                b'170199',
                                b'170199 Psychology not elsewhere classified',
                            ),
                            (b'1702', b'1702 COGNITIVE SCIENCES'),
                            (
                                b'170201',
                                b'170201 Computer Perception, Memory and Attention',
                            ),
                            (b'170202', b'170202 Decision Making'),
                            (
                                b'170203',
                                b'170203 Knowledge Representation and Machine Learning',
                            ),
                            (
                                b'170204',
                                b'170204 Linguistic Processes (incl. Speech Production and Comprehension)',
                            ),
                            (
                                b'170205',
                                b'170205 Neurocognitive Patterns and Neural Networks',
                            ),
                            (
                                b'170299',
                                b'170299 Cognitive Sciences not elsewhere classified',
                            ),
                            (
                                b'1799',
                                b'1799 OTHER PSYCHOLOGY AND COGNITIVE SCIENCES',
                            ),
                            (
                                b'179999',
                                b'179999 Psychology and Cognitive Sciences not elsewhere classified',
                            ),
                            (b'18', b'18 LAW AND LEGAL STUDIES'),
                            (b'1801', b'1801 LAW'),
                            (
                                b'180101',
                                b'180101 Aboriginal and Torres Strait Islander Law',
                            ),
                            (b'180102', b'180102 Access to Justice'),
                            (b'180103', b'180103 Administrative Law'),
                            (b'180104', b'180104 Civil Law and Procedure'),
                            (b'180105', b'180105 Commercial and Contract Law'),
                            (b'180106', b'180106 Comparative Law'),
                            (
                                b'180107',
                                b'180107 Conflict of Laws (Private International Law)',
                            ),
                            (b'180108', b'180108 Constitutional Law'),
                            (
                                b'180109',
                                b'180109 Corporations and Associations Law',
                            ),
                            (b'180110', b'180110 Criminal Law and Procedure'),
                            (
                                b'180111',
                                b'180111 Environmental and Natural Resources Law',
                            ),
                            (b'180112', b'180112 Equity and Trusts Law'),
                            (b'180113', b'180113 Family Law'),
                            (b'180114', b'180114 Human Rights Law'),
                            (b'180115', b'180115 Intellectual Property Law'),
                            (
                                b'180116',
                                b'180116 International Law (excl. International Trade Law)',
                            ),
                            (b'180117', b'180117 International Trade Law'),
                            (b'180118', b'180118 Labour Law'),
                            (b'180119', b'180119 Law and Society'),
                            (
                                b'180120',
                                b'180120 Legal Institutions (incl. Courts and Justice Systems)',
                            ),
                            (
                                b'180121',
                                b'180121 Legal Practice, Lawyering and the Legal Profession',
                            ),
                            (
                                b'180122',
                                b'180122 Legal Theory, Jurisprudence and Legal Interpretation',
                            ),
                            (
                                b'180123',
                                b'180123 Litigation, Adjudication and Dispute Resolution',
                            ),
                            (
                                b'180124',
                                b'180124 Property Law (excl. Intellectual Property Law)',
                            ),
                            (b'180125', b'180125 Taxation Law'),
                            (b'180126', b'180126 Tort Law'),
                            (
                                b'180199',
                                b'180199 Law not elsewhere classified',
                            ),
                            (b'1802', b'1802 MAORI LAW'),
                            (
                                b'180201',
                                b'180201 Nga Tikanga Maori (Maori Customary Law)',
                            ),
                            (
                                b'180202',
                                b'180202 Te Maori Whakahaere Rauemi (Maori Resource Law))',
                            ),
                            (
                                b'180203',
                                b'180203 Te Tiriti o Waitangi (The Treaty of Waitangi)',
                            ),
                            (
                                b'180204',
                                b'180204 Te Ture Whenua (Maori Land Law)',
                            ),
                            (
                                b'180299',
                                b'180299 Maori Law not elsewhere classified',
                            ),
                            (b'1899', b'1899 OTHER LAW AND LEGAL STUDIES'),
                            (
                                b'189999',
                                b'189999 Law and Legal Studies not elsewhere classified',
                            ),
                            (
                                b'19',
                                b'19 STUDIES IN CREATIVE ARTS AND WRITING',
                            ),
                            (b'1901', b'1901 ART THEORY AND CRITICISM'),
                            (b'190101', b'190101 Art Criticism'),
                            (b'190102', b'190102 Art History'),
                            (b'190103', b'190103 Art Theory'),
                            (b'190104', b'190104 Visual Cultures'),
                            (
                                b'190199',
                                b'190199 Art Theory and Criticism not elsewhere classified',
                            ),
                            (
                                b'1902',
                                b'1902 FILM, TELEVISION AND DIGITAL MEDIA',
                            ),
                            (b'190201', b'190201 Cinema Studies'),
                            (
                                b'190202',
                                b'190202 Computer Gaming and Animation',
                            ),
                            (b'190203', b'190203 Electronic Media Art'),
                            (b'190204', b'190204 Film and Television'),
                            (b'190205', b'190205 Interactive Media'),
                            (
                                b'190299',
                                b'190299 Film, Television and Digital Media not elsewhere classified',
                            ),
                            (
                                b'1903',
                                b'1903 JOURNALISM AND PROFESSIONAL WRITING',
                            ),
                            (b'190301', b'190301 Journalism Studies'),
                            (b'190302', b'190302 Professional Writing'),
                            (b'190303', b'190303 Technical Writing'),
                            (
                                b'190399',
                                b'190399 Journalism and Professional Writing not elsewhere classified',
                            ),
                            (
                                b'1904',
                                b'1904 PERFORMING ARTS AND CREATIVE WRITING',
                            ),
                            (
                                b'190401',
                                b'190401 Aboriginal and Torres Strait Islander Performing Arts',
                            ),
                            (
                                b'190402',
                                b'190402 Creative Writing (incl. Playwriting)',
                            ),
                            (b'190403', b'190403 Dance'),
                            (
                                b'190404',
                                b'190404 Drama, Theatre and Performance Studies',
                            ),
                            (b'190405', b'190405 Maori Performing Arts'),
                            (b'190406', b'190406 Music Composition'),
                            (b'190407', b'190407 Music Performance'),
                            (b'190408', b'190408 Music Therapy'),
                            (
                                b'190409',
                                b'190409 Musicology and Ethnomusicology',
                            ),
                            (
                                b'190410',
                                b'190410 Pacific Peoples Performing Arts',
                            ),
                            (
                                b'190499',
                                b'190499 Performing Arts and Creative Writing not elsewhere classified',
                            ),
                            (b'1905', b'1905 VISUAL ARTS AND CRAFTS'),
                            (b'190501', b'190501 Crafts'),
                            (
                                b'190502',
                                b'190502 Fine Arts (incl. Sculpture and Painting)',
                            ),
                            (b'190503', b'190503 Lens-based Practice'),
                            (
                                b'190504',
                                b'190504 Performance and Installation Art',
                            ),
                            (
                                b'190599',
                                b'190599 Visual Arts and Crafts not elsewhere classified',
                            ),
                            (
                                b'1999',
                                b'1999 OTHER STUDIES IN CREATIVE ARTS AND WRITING',
                            ),
                            (
                                b'199999',
                                b'199999 Studies in Creative Arts and Writing not elsewhere classified',
                            ),
                            (b'20', b'20 LANGUAGE, COMMUNICATION AND CULTURE'),
                            (b'2001', b'2001 COMMUNICATION AND MEDIA STUDIES'),
                            (b'200101', b'200101 Communication Studies'),
                            (
                                b'200102',
                                b'200102 Communication Technology and Digital Media Studies',
                            ),
                            (
                                b'200103',
                                b'200103 International and Development Communication',
                            ),
                            (b'200104', b'200104 Media Studies'),
                            (
                                b'200105',
                                b'200105 Organisational, Interpersonal and Intercultural Communication',
                            ),
                            (
                                b'200199',
                                b'200199 Communication and Media Studies not elsewhere classified',
                            ),
                            (b'2002', b'2002 CULTURAL STUDIES'),
                            (
                                b'200201',
                                b'200201 Aboriginal and Torres Strait Islander Cultural Studies',
                            ),
                            (b'200202', b'200202 Asian Cultural Studies'),
                            (
                                b'200203',
                                b'200203 Consumption and Everyday Life',
                            ),
                            (b'200204', b'200204 Cultural Theory'),
                            (b'200205', b'200205 Culture, Gender, Sexuality'),
                            (b'200206', b'200206 Globalisation and Culture'),
                            (b'200207', b'200207 Maori Cultural Studies'),
                            (b'200208', b'200208 Migrant Cultural Studies'),
                            (
                                b'200209',
                                b'200209 Multicultural, Intercultural and Cross-cultural Studies',
                            ),
                            (b'200210', b'200210 Pacific Cultural Studies'),
                            (b'200211', b'200211 Postcolonial Studies'),
                            (b'200212', b'200212 Screen and Media Culture'),
                            (
                                b'200299',
                                b'200299 Cultural Studies not elsewhere classified',
                            ),
                            (b'2003', b'2003 LANGUAGE STUDIES'),
                            (b'200301', b'200301 Early English Languages'),
                            (b'200302', b'200302 English Language'),
                            (
                                b'200303',
                                b'200303 English as a Second Language',
                            ),
                            (
                                b'200304',
                                b'200304 Central and Eastern European Languages (incl. Russian)',
                            ),
                            (
                                b'200305',
                                b'200305 Latin and Classical Greek Languages',
                            ),
                            (b'200306', b'200306 French Language'),
                            (b'200307', b'200307 German Language'),
                            (b'200308', b'200308 Iberian Languages'),
                            (b'200309', b'200309 Italian Language'),
                            (b'200310', b'200310 Other European Languages'),
                            (b'200311', b'200311 Chinese Languages'),
                            (b'200312', b'200312 Japanese Language'),
                            (b'200313', b'200313 Indonesian Languages'),
                            (
                                b'200314',
                                b'200314 South-East Asian Languages (excl. Indonesian)',
                            ),
                            (b'200315', b'200315 Indian Languages'),
                            (b'200316', b'200316 Korean Language'),
                            (
                                b'200317',
                                b'200317 Other Asian Languages (excl. South-East Asian)',
                            ),
                            (b'200318', b'200318 Middle Eastern Languages'),
                            (
                                b'200319',
                                b'200319 Aboriginal and Torres Strait Islander Languages',
                            ),
                            (b'200320', b'200320 Pacific Languages'),
                            (
                                b'200321',
                                b'200321 Te Reo Maori (Maori Language)',
                            ),
                            (
                                b'200322',
                                b'200322 Comparative Language Studies',
                            ),
                            (
                                b'200323',
                                b'200323 Translation and Interpretation Studies',
                            ),
                            (
                                b'200399',
                                b'200399 Language Studies not elsewhere classified',
                            ),
                            (b'2004', b'2004 LINGUISTICS'),
                            (
                                b'200401',
                                b'200401 Applied Linguistics and Educational Linguistics',
                            ),
                            (b'200402', b'200402 Computational Linguistics'),
                            (b'200403', b'200403 Discourse and Pragmatics'),
                            (
                                b'200404',
                                b'200404 Laboratory Phonetics and Speech Science',
                            ),
                            (
                                b'200405',
                                b'200405 Language in Culture and Society (Sociolinguistics)',
                            ),
                            (
                                b'200406',
                                b'200406 Language in Time and Space (incl. Historical Linguistics, Dialectology)',
                            ),
                            (b'200407', b'200407 Lexicography'),
                            (
                                b'200408',
                                b'200408 Linguistic Structures (incl. Grammar, Phonology, Lexicon, Semantics)',
                            ),
                            (
                                b'200499',
                                b'200499 Linguistics not elsewhere classified',
                            ),
                            (b'2005', b'2005 LITERARY STUDIES'),
                            (
                                b'200501',
                                b'200501 Aboriginal and Torres Strait Islander Literature',
                            ),
                            (
                                b'200502',
                                b'200502 Australian Literature (excl. Aboriginal and Torres Strait Islander Literature)',
                            ),
                            (
                                b'200503',
                                b'200503 British and Irish Literature',
                            ),
                            (b'200504', b'200504 Maori Literature'),
                            (
                                b'200505',
                                b'200505 New Zealand Literature (excl. Maori Literature)',
                            ),
                            (b'200506', b'200506 North American Literature'),
                            (b'200507', b'200507 Pacific Literature'),
                            (
                                b'200508',
                                b'200508 Other Literatures in English',
                            ),
                            (
                                b'200509',
                                b'200509 Central and Eastern European Literature (incl. Russian)',
                            ),
                            (
                                b'200510',
                                b'200510 Latin and Classical Greek Literature',
                            ),
                            (b'200511', b'200511 Literature in French'),
                            (b'200512', b'200512 Literature in German'),
                            (b'200513', b'200513 Literature in Italian'),
                            (
                                b'200514',
                                b'200514 Literature in Spanish and Portuguese',
                            ),
                            (b'200515', b'200515 Other European Literature'),
                            (b'200516', b'200516 Indonesian Literature'),
                            (b'200517', b'200517 Literature in Chinese'),
                            (b'200518', b'200518 Literature in Japanese'),
                            (
                                b'200519',
                                b'200519 South-East Asian Literature (excl. Indonesian)',
                            ),
                            (b'200520', b'200520 Indian Literature'),
                            (b'200521', b'200521 Korean Literature'),
                            (
                                b'200522',
                                b'200522 Other Asian Literature (excl. South-East Asian)',
                            ),
                            (b'200523', b'200523 Middle Eastern Literature'),
                            (
                                b'200524',
                                b'200524 Comparative Literature Studies',
                            ),
                            (b'200525', b'200525 Literary Theory'),
                            (
                                b'200526',
                                b'200526 Stylistics and Textual Analysis',
                            ),
                            (
                                b'200599',
                                b'200599 Literary Studies not elsewhere classified',
                            ),
                            (
                                b'2099',
                                b'2099 OTHER LANGUAGE, COMMUNICATION AND CULTURE',
                            ),
                            (
                                b'209999',
                                b'209999 Language, Communication and Culture not elsewhere classified',
                            ),
                            (b'21', b'21 HISTORY AND ARCHAEOLOGY'),
                            (b'2101', b'2101 ARCHAEOLOGY'),
                            (
                                b'210101',
                                b'210101 Aboriginal and Torres Strait Islander Archaeology',
                            ),
                            (b'210102', b'210102 Archaeological Science'),
                            (
                                b'210103',
                                b'210103 Archaeology of Asia, Africa and the Americas',
                            ),
                            (
                                b'210104',
                                b'210104 Archaeology of Australia (excl. Aboriginal and Torres Strait Islander)',
                            ),
                            (
                                b'210105',
                                b'210105 Archaeology of Europe, the Mediterranean and the Levant',
                            ),
                            (
                                b'210106',
                                b'210106 Archaeology of New Guinea and Pacific Islands (excl. New Zealand)',
                            ),
                            (
                                b'210107',
                                b'210107 Archaeology of New Zealand (excl. Maori)',
                            ),
                            (
                                b'210108',
                                b'210108 Historical Archaeology (incl. Industrial Archaeology)',
                            ),
                            (b'210109', b'210109 Maori Archaeology'),
                            (b'210110', b'210110 Maritime Archaeology'),
                            (
                                b'210199',
                                b'210199 Archaeology not elsewhere classified',
                            ),
                            (b'2102', b'2102 CURATORIAL AND RELATED STUDIES'),
                            (
                                b'210201',
                                b'210201 Archival, Repository and Related Studies',
                            ),
                            (
                                b'210202',
                                b'210202 Heritage and Cultural Conservation',
                            ),
                            (b'210203', b'210203 Materials Conservation'),
                            (b'210204', b'210204 Museum Studies'),
                            (
                                b'210299',
                                b'210299 Curatorial and Related Studies not elsewhere classified',
                            ),
                            (b'2103', b'2103 HISTORICAL STUDIES'),
                            (
                                b'210301',
                                b'210301 Aboriginal and Torres Strait Islander History',
                            ),
                            (b'210302', b'210302 Asian History'),
                            (
                                b'210303',
                                b'210303 Australian History (excl. Aboriginal and Torres Strait Islander History)',
                            ),
                            (b'210304', b'210304 Biography'),
                            (b'210305', b'210305 British History'),
                            (
                                b'210306',
                                b'210306 Classical Greek and Roman History',
                            ),
                            (
                                b'210307',
                                b'210307 European History (excl. British, Classical Greek and Roman)',
                            ),
                            (b'210308', b'210308 Latin American History'),
                            (b'210309', b'210309 Maori History'),
                            (
                                b'210310',
                                b'210310 Middle Eastern and African History',
                            ),
                            (b'210311', b'210311 New Zealand History'),
                            (b'210312', b'210312 North American History'),
                            (
                                b'210313',
                                b'210313 Pacific History (excl. New Zealand and Maori)',
                            ),
                            (
                                b'210399',
                                b'210399 Historical Studies not elsewhere classified',
                            ),
                            (b'2199', b'2199 OTHER HISTORY AND ARCHAEOLOGY'),
                            (
                                b'219999',
                                b'219999 History and Archaeology not elsewhere classified',
                            ),
                            (b'22', b'22 PHILOSOPHY AND RELIGIOUS STUDIES'),
                            (b'2201', b'2201 APPLIED ETHICS'),
                            (
                                b'220101',
                                b'220101 Bioethics (human and animal)',
                            ),
                            (b'220102', b'220102 Business Ethics'),
                            (
                                b'220103',
                                b'220103 Ethical Use of New Technology (e.g. Nanotechnology, Biotechnology)',
                            ),
                            (
                                b'220104',
                                b'220104 Human Rights and Justice Issues',
                            ),
                            (b'220105', b'220105 Legal Ethics'),
                            (b'220106', b'220106 Medical Ethics'),
                            (
                                b'220107',
                                b'220107 Professional Ethics (incl. police and research ethics)',
                            ),
                            (
                                b'220199',
                                b'220199 Applied Ethics not elsewhere classified',
                            ),
                            (
                                b'2202',
                                b'2202 HISTORY AND PHILOSOPHY OF SPECIFIC FIELDS',
                            ),
                            (b'220201', b'220201 Business and Labour History'),
                            (
                                b'220202',
                                b'220202 History and Philosophy of Education',
                            ),
                            (
                                b'220203',
                                b'220203 History and Philosophy of Engineering and Technology',
                            ),
                            (
                                b'220204',
                                b'220204 History and Philosophy of Law and Justice',
                            ),
                            (
                                b'220205',
                                b'220205 History and Philosophy of Medicine',
                            ),
                            (
                                b'220206',
                                b'220206 History and Philosophy of Science (incl. Non-historical Philosophy of Science)',
                            ),
                            (
                                b'220207',
                                b'220207 History and Philosophy of the Humanities',
                            ),
                        ],
                    ),
                ),
                (
                    'for_percentage_2',
                    models.IntegerField(
                        default=0,
                        help_text=b'The percentage',
                        choices=[
                            (0, b'0%'),
                            (10, b'10%'),
                            (20, b'20%'),
                            (30, b'30%'),
                            (40, b'40%'),
                            (50, b'50%'),
                            (60, b'60%'),
                            (70, b'70%'),
                            (80, b'80%'),
                            (90, b'90%'),
                            (100, b'100%'),
                        ],
                    ),
                ),
                (
                    'field_of_research_3',
                    models.CharField(
                        blank=True,
                        max_length=6,
                        null=True,
                        verbose_name=b'Third Field Of Research',
                        choices=[
                            (b'01', b'01 MATHEMATICAL SCIENCES'),
                            (b'0101', b'0101 PURE MATHEMATICS'),
                            (b'010101', b'010101 Algebra and Number Theory'),
                            (
                                b'010102',
                                b'010102 Algebraic and Differential Geometry',
                            ),
                            (
                                b'010103',
                                b'010103 Category Theory, K Theory, Homological Algebra',
                            ),
                            (
                                b'010104',
                                b'010104 Combinatorics and Discrete Mathematics (excl. Physical Combinatorics)',
                            ),
                            (
                                b'010105',
                                b'010105 Group Theory and Generalisations',
                            ),
                            (
                                b'010106',
                                b'010106 Lie Groups, Harmonic and Fourier Analysis',
                            ),
                            (
                                b'010107',
                                b'010107 Mathematical Logic, Set Theory, Lattices and Universal Algebra',
                            ),
                            (
                                b'010108',
                                b'010108 Operator Algebras and Functional Analysis',
                            ),
                            (
                                b'010109',
                                b'010109 Ordinary Differential Equations, Difference Equations and Dynamical Systems',
                            ),
                            (
                                b'010110',
                                b'010110 Partial Differential Equations',
                            ),
                            (
                                b'010111',
                                b'010111 Real and Complex Functions (incl. Several Variables)',
                            ),
                            (b'010112', b'010112 Topology'),
                            (
                                b'010199',
                                b'010199 Pure Mathematics not elsewhere classified',
                            ),
                            (b'0102', b'0102 APPLIED MATHEMATICS'),
                            (
                                b'010201',
                                b'010201 Approximation Theory and Asymptotic Methods',
                            ),
                            (b'010202', b'010202 Biological Mathematics'),
                            (
                                b'010203',
                                b'010203 Calculus of Variations, Systems Theory and Control Theory',
                            ),
                            (
                                b'010204',
                                b'010204 Dynamical Systems in Applications',
                            ),
                            (b'010205', b'010205 Financial Mathematics'),
                            (b'010206', b'010206 Operations Research'),
                            (
                                b'010207',
                                b'010207 Theoretical and Applied Mechanics',
                            ),
                            (
                                b'010299',
                                b'010299 Applied Mathematics not elsewhere classified',
                            ),
                            (
                                b'0103',
                                b'0103 NUMERICAL AND COMPUTATIONAL MATHEMATICS',
                            ),
                            (b'010301', b'010301 Numerical Analysis'),
                            (
                                b'010302',
                                b'010302 Numerical Solution of Differential and Integral Equations',
                            ),
                            (b'010303', b'010303 Optimisation'),
                            (
                                b'010399',
                                b'010399 Numerical and Computational Mathematics not elsewhere classified',
                            ),
                            (b'0104', b'0104 STATISTICS'),
                            (b'010401', b'010401 Applied Statistics'),
                            (b'010402', b'010402 Biostatistics'),
                            (b'010403', b'010403 Forensic Statistics'),
                            (b'010404', b'010404 Probability Theory'),
                            (b'010405', b'010405 Statistical Theory'),
                            (
                                b'010406',
                                b'010406 Stochastic Analysis and Modelling',
                            ),
                            (
                                b'010499',
                                b'010499 Statistics not elsewhere classified',
                            ),
                            (b'0105', b'0105 MATHEMATICAL PHYSICS'),
                            (
                                b'010501',
                                b'010501 Algebraic Structures in Mathematical Physics',
                            ),
                            (
                                b'010502',
                                b'010502 Integrable Systems (Classical and Quantum)',
                            ),
                            (
                                b'010503',
                                b'010503 Mathematical Aspects of Classical Mechanics, Quantum Mechanics and Quantum Information Theory',
                            ),
                            (
                                b'010504',
                                b'010504 Mathematical Aspects of General Relativity',
                            ),
                            (
                                b'010505',
                                b'010505 Mathematical Aspects of Quantum and Conformal Field Theory, Quantum Gravity and String Theory',
                            ),
                            (
                                b'010506',
                                b'010506 Statistical Mechanics, Physical Combinatorics and Mathematical Aspects of Condensed Matter',
                            ),
                            (
                                b'010599',
                                b'010599 Mathematical Physics not elsewhere classified',
                            ),
                            (b'0199', b'0199 OTHER MATHEMATICAL SCIENCES'),
                            (
                                b'019999',
                                b'019999 Mathematical Sciences not elsewhere classified',
                            ),
                            (b'02', b'02 PHYSICAL SCIENCES'),
                            (b'0201', b'0201 ASTRONOMICAL AND SPACE SCIENCES'),
                            (b'020101', b'020101 Astrobiology'),
                            (
                                b'020102',
                                b'020102 Astronomical and Space Instrumentation',
                            ),
                            (
                                b'020103',
                                b'020103 Cosmology and Extragalactic Astronomy',
                            ),
                            (b'020104', b'020104 Galactic Astronomy'),
                            (
                                b'020105',
                                b'020105 General Relativity and Gravitational Waves',
                            ),
                            (
                                b'020106',
                                b'020106 High Energy Astrophysics; Cosmic Rays',
                            ),
                            (
                                b'020107',
                                b'020107 Mesospheric, Ionospheric and Magnetospheric Physics',
                            ),
                            (
                                b'020108',
                                b'020108 Planetary Science (excl. Extraterrestrial Geology)',
                            ),
                            (b'020109', b'020109 Space and Solar Physics'),
                            (
                                b'020110',
                                b'020110 Stellar Astronomy and Planetary Systems',
                            ),
                            (
                                b'020199',
                                b'020199 Astronomical and Space Sciences not elsewhere classified',
                            ),
                            (
                                b'0202',
                                b'0202 ATOMIC, MOLECULAR, NUCLEAR, PARTICLE AND PLASMA PHYSICS',
                            ),
                            (
                                b'020201',
                                b'020201 Atomic and Molecular Physics',
                            ),
                            (b'020202', b'020202 Nuclear Physics'),
                            (b'020203', b'020203 Particle Physics'),
                            (
                                b'020204',
                                b'020204 Plasma Physics; Fusion Plasmas; Electrical Discharges',
                            ),
                            (
                                b'020299',
                                b'020299 Atomic, Molecular, Nuclear, Particle and Plasma Physics not elsewhere classified',
                            ),
                            (b'0203', b'0203 CLASSICAL PHYSICS'),
                            (
                                b'020301',
                                b'020301 Acoustics and Acoustical Devices; Waves',
                            ),
                            (
                                b'020302',
                                b'020302 Electrostatics and Electrodynamics',
                            ),
                            (b'020303', b'020303 Fluid Physics'),
                            (
                                b'020304',
                                b'020304 Thermodynamics and Statistical Physics',
                            ),
                            (
                                b'020399',
                                b'020399 Classical Physics not elsewhere classified',
                            ),
                            (b'0204', b'0204 CONDENSED MATTER PHYSICS'),
                            (
                                b'020401',
                                b'020401 Condensed Matter Characterisation Technique Development',
                            ),
                            (b'020402', b'020402 Condensed Matter Imaging'),
                            (
                                b'020403',
                                b'020403 Condensed Matter Modelling and Density Functional Theory',
                            ),
                            (
                                b'020404',
                                b'020404 Electronic and Magnetic Properties of Condensed Matter; Superconductivity',
                            ),
                            (b'020405', b'020405 Soft Condensed Matter'),
                            (
                                b'020406',
                                b'020406 Surfaces and Structural Properties of Condensed Matter',
                            ),
                            (
                                b'020499',
                                b'020499 Condensed Matter Physics not elsewhere classified',
                            ),
                            (b'0205', b'0205 OPTICAL PHYSICS'),
                            (
                                b'020501',
                                b'020501 Classical and Physical Optics',
                            ),
                            (
                                b'020502',
                                b'020502 Lasers and Quantum Electronics',
                            ),
                            (
                                b'020503',
                                b'020503 Nonlinear Optics and Spectroscopy',
                            ),
                            (
                                b'020504',
                                b'020504 Photonics, Optoelectronics and Optical Communications',
                            ),
                            (
                                b'020599',
                                b'020599 Optical Physics not elsewhere classified',
                            ),
                            (b'0206', b'0206 QUANTUM PHYSICS'),
                            (
                                b'020601',
                                b'020601 Degenerate Quantum Gases and Atom Optics',
                            ),
                            (
                                b'020602',
                                b'020602 Field Theory and String Theory',
                            ),
                            (
                                b'020603',
                                b'020603 Quantum Information, Computation and Communication',
                            ),
                            (b'020604', b'020604 Quantum Optics'),
                            (
                                b'020699',
                                b'020699 Quantum Physics not elsewhere classified',
                            ),
                            (b'0299', b'0299 OTHER PHYSICAL SCIENCES'),
                            (b'029901', b'029901 Biological Physics'),
                            (b'029902', b'029902 Complex Physical Systems'),
                            (b'029903', b'029903 Medical Physics'),
                            (
                                b'029904',
                                b'029904 Synchrotrons; Accelerators; Instruments and Techniques',
                            ),
                            (
                                b'029999',
                                b'029999 Physical Sciences not elsewhere classified',
                            ),
                            (b'03', b'03 CHEMICAL SCIENCES'),
                            (b'0301', b'0301 ANALYTICAL CHEMISTRY'),
                            (b'030101', b'030101 Analytical Spectrometry'),
                            (b'030102', b'030102 Electroanalytical Chemistry'),
                            (b'030103', b'030103 Flow Analysis'),
                            (
                                b'030104',
                                b'030104 Immunological and Bioassay Methods',
                            ),
                            (
                                b'030105',
                                b'030105 Instrumental Methods (excl. Immunological and Bioassay Methods)',
                            ),
                            (
                                b'030106',
                                b'030106 Quality Assurance, Chemometrics, Traceability and Metrological Chemistry',
                            ),
                            (
                                b'030107',
                                b'030107 Sensor Technology (Chemical aspects)',
                            ),
                            (b'030108', b'030108 Separation Science'),
                            (
                                b'030199',
                                b'030199 Analytical Chemistry not elsewhere classified',
                            ),
                            (b'0302', b'0302 INORGANIC CHEMISTRY'),
                            (b'030201', b'030201 Bioinorganic Chemistry'),
                            (b'030202', b'030202 f-Block Chemistry'),
                            (b'030203', b'030203 Inorganic Green Chemistry'),
                            (b'030204', b'030204 Main Group Metal Chemistry'),
                            (b'030205', b'030205 Non-metal Chemistry'),
                            (b'030206', b'030206 Solid State Chemistry'),
                            (b'030207', b'030207 Transition Metal Chemistry'),
                            (
                                b'030299',
                                b'030299 Inorganic Chemistry not elsewhere classified',
                            ),
                            (
                                b'0303',
                                b'0303 MACROMOLECULAR AND MATERIALS CHEMISTRY',
                            ),
                            (
                                b'030301',
                                b'030301 Chemical Characterisation of Materials',
                            ),
                            (
                                b'030302',
                                b'030302 Nanochemistry and Supramolecular Chemistry',
                            ),
                            (
                                b'030303',
                                b'030303 Optical Properties of Materials',
                            ),
                            (
                                b'030304',
                                b'030304 Physical Chemistry of Materials',
                            ),
                            (b'030305', b'030305 Polymerisation Mechanisms'),
                            (b'030306', b'030306 Synthesis of Materials'),
                            (
                                b'030307',
                                b'030307 Theory and Design of Materials',
                            ),
                            (
                                b'030399',
                                b'030399 Macromolecular and Materials Chemistry not elsewhere classified',
                            ),
                            (
                                b'0304',
                                b'0304 MEDICINAL AND BIOMOLECULAR CHEMISTRY',
                            ),
                            (
                                b'030401',
                                b'030401 Biologically Active Molecules',
                            ),
                            (
                                b'030402',
                                b'030402 Biomolecular Modelling and Design',
                            ),
                            (
                                b'030403',
                                b'030403 Characterisation of Biological Macromolecules',
                            ),
                            (
                                b'030404',
                                b'030404 Cheminformatics and Quantitative Structure-Activity Relationships',
                            ),
                            (b'030405', b'030405 Molecular Medicine'),
                            (b'030406', b'030406 Proteins and Peptides'),
                            (
                                b'030499',
                                b'030499 Medicinal and Biomolecular Chemistry not elsewhere classified',
                            ),
                            (b'0305', b'0305 ORGANIC CHEMISTRY'),
                            (b'030501', b'030501 Free Radical Chemistry'),
                            (b'030502', b'030502 Natural Products Chemistry'),
                            (b'030503', b'030503 Organic Chemical Synthesis'),
                            (b'030504', b'030504 Organic Green Chemistry'),
                            (b'030505', b'030505 Physical Organic Chemistry'),
                            (
                                b'030599',
                                b'030599 Organic Chemistry not elsewhere classified',
                            ),
                            (
                                b'0306',
                                b'0306 PHYSICAL CHEMISTRY (INCL. STRUCTURAL)',
                            ),
                            (
                                b'030601',
                                b'030601 Catalysis and Mechanisms of Reactions',
                            ),
                            (
                                b'030602',
                                b'030602 Chemical Thermodynamics and Energetics',
                            ),
                            (
                                b'030603',
                                b'030603 Colloid and Surface Chemistry',
                            ),
                            (b'030604', b'030604 Electrochemistry'),
                            (b'030605', b'030605 Solution Chemistry'),
                            (
                                b'030606',
                                b'030606 Structural Chemistry and Spectroscopy',
                            ),
                            (
                                b'030607',
                                b'030607 Transport Properties and Non-equilibrium Processes',
                            ),
                            (
                                b'030699',
                                b'030699 Physical Chemistry not elsewhere classified',
                            ),
                            (
                                b'0307',
                                b'0307 THEORETICAL AND COMPUTATIONAL CHEMISTRY',
                            ),
                            (b'030701', b'030701 Quantum Chemistry'),
                            (b'030702', b'030702 Radiation and Matter'),
                            (
                                b'030703',
                                b'030703 Reaction Kinetics and Dynamics',
                            ),
                            (
                                b'030704',
                                b'030704 Statistical Mechanics in Chemistry',
                            ),
                            (
                                b'030799',
                                b'030799 Theoretical and Computational Chemistry not elsewhere classified',
                            ),
                            (b'0399', b'0399 OTHER CHEMICAL SCIENCES'),
                            (
                                b'039901',
                                b'039901 Environmental Chemistry (incl. Atmospheric Chemistry)',
                            ),
                            (b'039902', b'039902 Forensic Chemistry'),
                            (b'039903', b'039903 Industrial Chemistry'),
                            (b'039904', b'039904 Organometallic Chemistry'),
                            (
                                b'039999',
                                b'039999 Chemical Sciences not elsewhere classified',
                            ),
                            (b'04', b'04 EARTH SCIENCES'),
                            (b'0401', b'0401 ATMOSPHERIC SCIENCES'),
                            (b'040101', b'040101 Atmospheric Aerosols'),
                            (b'040102', b'040102 Atmospheric Dynamics'),
                            (b'040103', b'040103 Atmospheric Radiation'),
                            (b'040104', b'040104 Climate Change Processes'),
                            (
                                b'040105',
                                b'040105 Climatology (excl. Climate Change Processes)',
                            ),
                            (b'040106', b'040106 Cloud Physics'),
                            (b'040107', b'040107 Meteorology'),
                            (
                                b'040108',
                                b'040108 Tropospheric and Stratospheric Physics',
                            ),
                            (
                                b'040199',
                                b'040199 Atmospheric Sciences not elsewhere classified',
                            ),
                            (b'0402', b'0402 GEOCHEMISTRY'),
                            (b'040201', b'040201 Exploration Geochemistry'),
                            (b'040202', b'040202 Inorganic Geochemistry'),
                            (b'040203', b'040203 Isotope Geochemistry'),
                            (b'040204', b'040204 Organic Geochemistry'),
                            (
                                b'040299',
                                b'040299 Geochemistry not elsewhere classified',
                            ),
                            (b'0403', b'0403 GEOLOGY'),
                            (b'040301', b'040301 Basin Analysis'),
                            (b'040302', b'040302 Extraterrestrial Geology'),
                            (b'040303', b'040303 Geochronology'),
                            (
                                b'040304',
                                b'040304 Igneous and Metamorphic Petrology',
                            ),
                            (b'040305', b'040305 Marine Geoscience'),
                            (
                                b'040306',
                                b'040306 Mineralogy and Crystallography',
                            ),
                            (b'040307', b'040307 Ore Deposit Petrology'),
                            (
                                b'040308',
                                b'040308 Palaeontology (incl. Palynology)',
                            ),
                            (b'040309', b'040309 Petroleum and Coal Geology'),
                            (b'040310', b'040310 Sedimentology'),
                            (
                                b'040311',
                                b'040311 Stratigraphy (incl. Biostratigraphy and Sequence Stratigraphy)',
                            ),
                            (b'040312', b'040312 Structural Geology'),
                            (b'040313', b'040313 Tectonics'),
                            (b'040314', b'040314 Volcanology'),
                            (
                                b'040399',
                                b'040399 Geology not elsewhere classified',
                            ),
                            (b'0404', b'0404 GEOPHYSICS'),
                            (
                                b'040401',
                                b'040401 Electrical and Electromagnetic Methods in Geophysics',
                            ),
                            (b'040402', b'040402 Geodynamics'),
                            (b'040403', b'040403 Geophysical Fluid Dynamics'),
                            (
                                b'040404',
                                b'040404 Geothermics and Radiometrics',
                            ),
                            (b'040405', b'040405 Gravimetrics'),
                            (
                                b'040406',
                                b'040406 Magnetism and Palaeomagnetism',
                            ),
                            (
                                b'040407',
                                b'040407 Seismology and Seismic Exploration',
                            ),
                            (
                                b'040499',
                                b'040499 Geophysics not elsewhere classified',
                            ),
                            (b'0405', b'0405 OCEANOGRAPHY'),
                            (b'040501', b'040501 Biological Oceanography'),
                            (b'040502', b'040502 Chemical Oceanography'),
                            (b'040503', b'040503 Physical Oceanography'),
                            (
                                b'040599',
                                b'040599 Oceanography not elsewhere classified',
                            ),
                            (
                                b'0406',
                                b'0406 PHYSICAL GEOGRAPHY AND ENVIRONMENTAL GEOSCIENCE',
                            ),
                            (
                                b'040601',
                                b'040601 Geomorphology and Regolith and Landscape Evolution',
                            ),
                            (b'040602', b'040602 Glaciology'),
                            (b'040603', b'040603 Hydrogeology'),
                            (b'040604', b'040604 Natural Hazards'),
                            (b'040605', b'040605 Palaeoclimatology'),
                            (b'040606', b'040606 Quaternary Environments'),
                            (b'040607', b'040607 Surface Processes'),
                            (b'040608', b'040608 Surfacewater Hydrology'),
                            (
                                b'040699',
                                b'040699 Physical Geography and Environmental Geoscience not elsewhere classified',
                            ),
                            (b'0499', b'0499 OTHER EARTH SCIENCES'),
                            (
                                b'049999',
                                b'049999 Earth Sciences not elsewhere classified',
                            ),
                            (b'05', b'05 ENVIRONMENTAL SCIENCES'),
                            (b'0501', b'0501 ECOLOGICAL APPLICATIONS'),
                            (
                                b'050101',
                                b'050101 Ecological Impacts of Climate Change',
                            ),
                            (b'050102', b'050102 Ecosystem Function'),
                            (b'050103', b'050103 Invasive Species Ecology'),
                            (b'050104', b'050104 Landscape Ecology'),
                            (
                                b'050199',
                                b'050199 Ecological Applications not elsewhere classified',
                            ),
                            (
                                b'0502',
                                b'0502 ENVIRONMENTAL SCIENCE AND MANAGEMENT',
                            ),
                            (
                                b'050201',
                                b'050201 Aboriginal and Torres Strait Islander Environmental Knowledge',
                            ),
                            (
                                b'050202',
                                b'050202 Conservation and Biodiversity',
                            ),
                            (
                                b'050203',
                                b'050203 Environmental Education and Extension',
                            ),
                            (
                                b'050204',
                                b'050204 Environmental Impact Assessment',
                            ),
                            (b'050205', b'050205 Environmental Management'),
                            (b'050206', b'050206 Environmental Monitoring'),
                            (
                                b'050207',
                                b'050207 Environmental Rehabilitation (excl. Bioremediation)',
                            ),
                            (
                                b'050208',
                                b'050208 Maori Environmental Knowledge',
                            ),
                            (b'050209', b'050209 Natural Resource Management'),
                            (
                                b'050210',
                                b'050210 Pacific Peoples Environmental Knowledge',
                            ),
                            (
                                b'050211',
                                b'050211 Wildlife and Habitat Management',
                            ),
                            (
                                b'050299',
                                b'050299 Environmental Science and Management not elsewhere classified',
                            ),
                            (b'0503', b'0503 SOIL SCIENCES'),
                            (
                                b'050301',
                                b'050301 Carbon Sequestration Science',
                            ),
                            (
                                b'050302',
                                b'050302 Land Capability and Soil Degradation',
                            ),
                            (b'050303', b'050303 Soil Biology'),
                            (
                                b'050304',
                                b'050304 Soil Chemistry (excl. Carbon Sequestration Science)',
                            ),
                            (b'050305', b'050305 Soil Physics'),
                            (
                                b'050399',
                                b'050399 Soil Sciences not elsewhere classified',
                            ),
                            (b'0599', b'0599 OTHER ENVIRONMENTAL SCIENCES'),
                            (
                                b'059999',
                                b'059999 Environmental Sciences not elsewhere classified',
                            ),
                            (b'06', b'06 BIOLOGICAL SCIENCES'),
                            (b'0601', b'0601 BIOCHEMISTRY AND CELL BIOLOGY'),
                            (b'060101', b'060101 Analytical Biochemistry'),
                            (b'060102', b'060102 Bioinformatics'),
                            (
                                b'060103',
                                b'060103 Cell Development, Proliferation and Death',
                            ),
                            (b'060104', b'060104 Cell Metabolism'),
                            (b'060105', b'060105 Cell Neurochemistry'),
                            (
                                b'060106',
                                b'060106 Cellular Interactions (incl. Adhesion, Matrix, Cell Wall)',
                            ),
                            (b'060107', b'060107 Enzymes'),
                            (b'060108', b'060108 Protein Trafficking'),
                            (
                                b'060109',
                                b'060109 Proteomics and Intermolecular Interactions (excl. Medical Proteomics)',
                            ),
                            (
                                b'060110',
                                b'060110 Receptors and Membrane Biology',
                            ),
                            (b'060111', b'060111 Signal Transduction'),
                            (
                                b'060112',
                                b'060112 Structural Biology (incl. Macromolecular Modelling)',
                            ),
                            (b'060113', b'060113 Synthetic Biology'),
                            (b'060114', b'060114 Systems Biology'),
                            (
                                b'060199',
                                b'060199 Biochemistry and Cell Biology not elsewhere classified',
                            ),
                            (b'0602', b'0602 ECOLOGY'),
                            (b'060201', b'060201 Behavioural Ecology'),
                            (
                                b'060202',
                                b'060202 Community Ecology (excl. Invasive Species Ecology)',
                            ),
                            (b'060203', b'060203 Ecological Physiology'),
                            (b'060204', b'060204 Freshwater Ecology'),
                            (
                                b'060205',
                                b'060205 Marine and Estuarine Ecology (incl. Marine Ichthyology)',
                            ),
                            (b'060206', b'060206 Palaeoecology'),
                            (b'060207', b'060207 Population Ecology'),
                            (b'060208', b'060208 Terrestrial Ecology'),
                            (
                                b'060299',
                                b'060299 Ecology not elsewhere classified',
                            ),
                            (b'0603', b'0603 EVOLUTIONARY BIOLOGY'),
                            (
                                b'060301',
                                b'060301 Animal Systematics and Taxonomy',
                            ),
                            (
                                b'060302',
                                b'060302 Biogeography and Phylogeography',
                            ),
                            (b'060303', b'060303 Biological Adaptation'),
                            (b'060304', b'060304 Ethology and Sociobiology'),
                            (
                                b'060305',
                                b'060305 Evolution of Developmental Systems',
                            ),
                            (
                                b'060306',
                                b'060306 Evolutionary Impacts of Climate Change',
                            ),
                            (b'060307', b'060307 Host-Parasite Interactions'),
                            (b'060308', b'060308 Life Histories'),
                            (
                                b'060309',
                                b'060309 Phylogeny and Comparative Analysis',
                            ),
                            (
                                b'060310',
                                b'060310 Plant Systematics and Taxonomy',
                            ),
                            (b'060311', b'060311 Speciation and Extinction'),
                            (
                                b'060399',
                                b'060399 Evolutionary Biology not elsewhere classified',
                            ),
                            (b'0604', b'0604 GENETICS'),
                            (b'060401', b'060401 Anthropological Genetics'),
                            (b'060402', b'060402 Cell and Nuclear Division'),
                            (
                                b'060403',
                                b'060403 Developmental Genetics (incl. Sex Determination)',
                            ),
                            (
                                b'060404',
                                b'060404 Epigenetics (incl. Genome Methylation and Epigenomics)',
                            ),
                            (
                                b'060405',
                                b'060405 Gene Expression (incl. Microarray and other genome-wide approaches)',
                            ),
                            (b'060406', b'060406 Genetic Immunology'),
                            (
                                b'060407',
                                b'060407 Genome Structure and Regulation',
                            ),
                            (b'060408', b'060408 Genomics'),
                            (b'060409', b'060409 Molecular Evolution'),
                            (b'060410', b'060410 Neurogenetics'),
                            (
                                b'060411',
                                b'060411 Population, Ecological and Evolutionary Genetics',
                            ),
                            (
                                b'060412',
                                b'060412 Quantitative Genetics (incl. Disease and Trait Mapping Genetics)',
                            ),
                            (
                                b'060499',
                                b'060499 Genetics not elsewhere classified',
                            ),
                            (b'0605', b'0605 MICROBIOLOGY'),
                            (b'060501', b'060501 Bacteriology'),
                            (b'060502', b'060502 Infectious Agents'),
                            (b'060503', b'060503 Microbial Genetics'),
                            (b'060504', b'060504 Microbial Ecology'),
                            (b'060505', b'060505 Mycology'),
                            (b'060506', b'060506 Virology'),
                            (
                                b'060599',
                                b'060599 Microbiology not elsewhere classified',
                            ),
                            (b'0606', b'0606 PHYSIOLOGY'),
                            (
                                b'060601',
                                b'060601 Animal Physiology - Biophysics',
                            ),
                            (b'060602', b'060602 Animal Physiology - Cell'),
                            (b'060603', b'060603 Animal Physiology - Systems'),
                            (b'060604', b'060604 Comparative Physiology'),
                            (
                                b'060699',
                                b'060699 Physiology not elsewhere classified',
                            ),
                            (b'0607', b'0607 PLANT BIOLOGY'),
                            (
                                b'060701',
                                b'060701 Phycology (incl. Marine Grasses)',
                            ),
                            (
                                b'060702',
                                b'060702 Plant Cell and Molecular Biology',
                            ),
                            (
                                b'060703',
                                b'060703 Plant Developmental and Reproductive Biology',
                            ),
                            (b'060704', b'060704 Plant Pathology'),
                            (b'060705', b'060705 Plant Physiology'),
                            (
                                b'060799',
                                b'060799 Plant Biology not elsewhere classified',
                            ),
                            (b'0608', b'0608 ZOOLOGY'),
                            (b'060801', b'060801 Animal Behaviour'),
                            (
                                b'060802',
                                b'060802 Animal Cell and Molecular Biology',
                            ),
                            (
                                b'060803',
                                b'060803 Animal Developmental and Reproductive Biology',
                            ),
                            (b'060804', b'060804 Animal Immunology'),
                            (b'060805', b'060805 Animal Neurobiology'),
                            (
                                b'060806',
                                b'060806 Animal Physiological Ecology',
                            ),
                            (
                                b'060807',
                                b'060807 Animal Structure and Function',
                            ),
                            (b'060808', b'060808 Invertebrate Biology'),
                            (b'060809', b'060809 Vertebrate Biology'),
                            (
                                b'060899',
                                b'060899 Zoology not elsewhere classified',
                            ),
                            (b'0699', b'0699 OTHER BIOLOGICAL SCIENCES'),
                            (b'069901', b'069901 Forensic Biology'),
                            (b'069902', b'069902 Global Change Biology'),
                            (
                                b'069999',
                                b'069999 Biological Sciences not elsewhere classified',
                            ),
                            (
                                b'07',
                                b'07 AGRICULTURAL AND VETERINARY SCIENCES',
                            ),
                            (
                                b'0701',
                                b'0701 AGRICULTURE, LAND AND FARM MANAGEMENT',
                            ),
                            (
                                b'070101',
                                b'070101 Agricultural Land Management',
                            ),
                            (b'070102', b'070102 Agricultural Land Planning'),
                            (
                                b'070103',
                                b'070103 Agricultural Production Systems Simulation',
                            ),
                            (
                                b'070104',
                                b'070104 Agricultural Spatial Analysis and Modelling',
                            ),
                            (
                                b'070105',
                                b'070105 Agricultural Systems Analysis and Modelling',
                            ),
                            (
                                b'070106',
                                b'070106 Farm Management, Rural Management and Agribusiness',
                            ),
                            (b'070107', b'070107 Farming Systems Research'),
                            (
                                b'070108',
                                b'070108 Sustainable Agricultural Development',
                            ),
                            (
                                b'070199',
                                b'070199 Agriculture, Land and Farm Management not elsewhere classified',
                            ),
                            (b'0702', b'0702 ANIMAL PRODUCTION'),
                            (b'070201', b'070201 Animal Breeding'),
                            (
                                b'070202',
                                b'070202 Animal Growth and Development',
                            ),
                            (b'070203', b'070203 Animal Management'),
                            (b'070204', b'070204 Animal Nutrition'),
                            (
                                b'070205',
                                b'070205 Animal Protection (Pests and Pathogens)',
                            ),
                            (b'070206', b'070206 Animal Reproduction'),
                            (b'070207', b'070207 Humane Animal Treatment'),
                            (
                                b'070299',
                                b'070299 Animal Production not elsewhere classified',
                            ),
                            (b'0703', b'0703 CROP AND PASTURE PRODUCTION'),
                            (
                                b'070301',
                                b'070301 Agro-ecosystem Function and Prediction',
                            ),
                            (b'070302', b'070302 Agronomy'),
                            (
                                b'070303',
                                b'070303 Crop and Pasture Biochemistry and Physiology',
                            ),
                            (
                                b'070304',
                                b'070304 Crop and Pasture Biomass and Bioproducts',
                            ),
                            (
                                b'070305',
                                b'070305 Crop and Pasture Improvement (Selection and Breeding)',
                            ),
                            (b'070306', b'070306 Crop and Pasture Nutrition'),
                            (
                                b'070307',
                                b'070307 Crop and Pasture Post Harvest Technologies (incl. Transportation and Storage)',
                            ),
                            (
                                b'070308',
                                b'070308 Crop and Pasture Protection (Pests, Diseases and Weeds)',
                            ),
                            (
                                b'070399',
                                b'070399 Crop and Pasture Production not elsewhere classified',
                            ),
                            (b'0704', b'0704 FISHERIES SCIENCES'),
                            (b'070401', b'070401 Aquaculture'),
                            (
                                b'070402',
                                b'070402 Aquatic Ecosystem Studies and Stock Assessment',
                            ),
                            (b'070403', b'070403 Fisheries Management'),
                            (b'070404', b'070404 Fish Pests and Diseases'),
                            (
                                b'070405',
                                b'070405 Fish Physiology and Genetics',
                            ),
                            (
                                b'070406',
                                b'070406 Post-Harvest Fisheries Technologies (incl. Transportation)',
                            ),
                            (
                                b'070499',
                                b'070499 Fisheries Sciences not elsewhere classified',
                            ),
                            (b'0705', b'0705 FORESTRY SCIENCES'),
                            (b'070501', b'070501 Agroforestry'),
                            (
                                b'070502',
                                b'070502 Forestry Biomass and Bioproducts',
                            ),
                            (b'070503', b'070503 Forestry Fire Management'),
                            (
                                b'070504',
                                b'070504 Forestry Management and Environment',
                            ),
                            (
                                b'070505',
                                b'070505 Forestry Pests, Health and Diseases',
                            ),
                            (
                                b'070506',
                                b'070506 Forestry Product Quality Assessment',
                            ),
                            (
                                b'070507',
                                b'070507 Tree Improvement (Selection and Breeding)',
                            ),
                            (
                                b'070508',
                                b'070508 Tree Nutrition and Physiology',
                            ),
                            (b'070509', b'070509 Wood Fibre Processing'),
                            (b'070510', b'070510 Wood Processing'),
                            (
                                b'070599',
                                b'070599 Forestry Sciences not elsewhere classified',
                            ),
                            (b'0706', b'0706 HORTICULTURAL PRODUCTION'),
                            (
                                b'070601',
                                b'070601 Horticultural Crop Growth and Development',
                            ),
                            (
                                b'070602',
                                b'070602 Horticultural Crop Improvement (Selection and Breeding)',
                            ),
                            (
                                b'070603',
                                b'070603 Horticultural Crop Protection (Pests, Diseases and Weeds)',
                            ),
                            (b'070604', b'070604 Oenology and Viticulture'),
                            (
                                b'070605',
                                b'070605 Post Harvest Horticultural Technologies (incl. Transportation and Storage)',
                            ),
                            (
                                b'070699',
                                b'070699 Horticultural Production not elsewhere classified',
                            ),
                            (b'0707', b'0707 VETERINARY SCIENCES'),
                            (
                                b'070701',
                                b'070701 Veterinary Anaesthesiology and Intensive Care',
                            ),
                            (
                                b'070702',
                                b'070702 Veterinary Anatomy and Physiology',
                            ),
                            (
                                b'070703',
                                b'070703 Veterinary Diagnosis and Diagnostics',
                            ),
                            (b'070704', b'070704 Veterinary Epidemiology'),
                            (b'070705', b'070705 Veterinary Immunology'),
                            (b'070706', b'070706 Veterinary Medicine'),
                            (
                                b'070707',
                                b'070707 Veterinary Microbiology (excl. Virology)',
                            ),
                            (b'070708', b'070708 Veterinary Parasitology'),
                            (b'070709', b'070709 Veterinary Pathology'),
                            (b'070710', b'070710 Veterinary Pharmacology'),
                            (b'070711', b'070711 Veterinary Surgery'),
                            (b'070712', b'070712 Veterinary Virology'),
                            (
                                b'070799',
                                b'070799 Veterinary Sciences not elsewhere classified',
                            ),
                            (
                                b'0799',
                                b'0799 OTHER AGRICULTURAL AND VETERINARY SCIENCES',
                            ),
                            (
                                b'079901',
                                b'079901 Agricultural Hydrology (Drainage, Flooding, Irrigation, Quality, etc.)',
                            ),
                            (
                                b'079902',
                                b'079902 Fertilisers and Agrochemicals (incl. Application)',
                            ),
                            (
                                b'079999',
                                b'079999 Agricultural and Veterinary Sciences not elsewhere classified',
                            ),
                            (b'08', b'08 INFORMATION AND COMPUTING SCIENCES'),
                            (
                                b'0801',
                                b'0801 ARTIFICIAL INTELLIGENCE AND IMAGE PROCESSING',
                            ),
                            (
                                b'080101',
                                b'080101 Adaptive Agents and Intelligent Robotics',
                            ),
                            (b'080102', b'080102 Artificial Life'),
                            (b'080103', b'080103 Computer Graphics'),
                            (b'080104', b'080104 Computer Vision'),
                            (b'080105', b'080105 Expert Systems'),
                            (b'080106', b'080106 Image Processing'),
                            (b'080107', b'080107 Natural Language Processing'),
                            (
                                b'080108',
                                b'080108 Neural, Evolutionary and Fuzzy Computation',
                            ),
                            (
                                b'080109',
                                b'080109 Pattern Recognition and Data Mining',
                            ),
                            (b'080110', b'080110 Simulation and Modelling'),
                            (
                                b'080111',
                                b'080111 Virtual Reality and Related Simulation',
                            ),
                            (
                                b'080199',
                                b'080199 Artificial Intelligence and Image Processing not elsewhere classified',
                            ),
                            (
                                b'0802',
                                b'0802 COMPUTATION THEORY AND MATHEMATICS',
                            ),
                            (
                                b'080201',
                                b'080201 Analysis of Algorithms and Complexity',
                            ),
                            (
                                b'080202',
                                b'080202 Applied Discrete Mathematics',
                            ),
                            (
                                b'080203',
                                b'080203 Computational Logic and Formal Languages',
                            ),
                            (b'080204', b'080204 Mathematical Software'),
                            (b'080205', b'080205 Numerical Computation'),
                            (
                                b'080299',
                                b'080299 Computation Theory and Mathematics not elsewhere classified',
                            ),
                            (b'0803', b'0803 COMPUTER SOFTWARE'),
                            (b'080301', b'080301 Bioinformatics Software'),
                            (
                                b'080302',
                                b'080302 Computer System Architecture',
                            ),
                            (b'080303', b'080303 Computer System Security'),
                            (b'080304', b'080304 Concurrent Programming'),
                            (b'080305', b'080305 Multimedia Programming'),
                            (b'080306', b'080306 Open Software'),
                            (b'080307', b'080307 Operating Systems'),
                            (b'080308', b'080308 Programming Languages'),
                            (b'080309', b'080309 Software Engineering'),
                            (
                                b'080399',
                                b'080399 Computer Software not elsewhere classified',
                            ),
                            (b'0804', b'0804 DATA FORMAT'),
                            (
                                b'080401',
                                b'080401 Coding and Information Theory',
                            ),
                            (b'080402', b'080402 Data Encryption'),
                            (b'080403', b'080403 Data Structures'),
                            (b'080404', b'080404 Markup Languages'),
                            (
                                b'080499',
                                b'080499 Data Format not elsewhere classified',
                            ),
                            (b'0805', b'0805 DISTRIBUTED COMPUTING'),
                            (
                                b'080501',
                                b'080501 Distributed and Grid Systems',
                            ),
                            (b'080502', b'080502 Mobile Technologies'),
                            (
                                b'080503',
                                b'080503 Networking and Communications',
                            ),
                            (b'080504', b'080504 Ubiquitous Computing'),
                            (
                                b'080505',
                                b'080505 Web Technologies (excl. Web Search)',
                            ),
                            (
                                b'080599',
                                b'080599 Distributed Computing not elsewhere classified',
                            ),
                            (b'0806', b'0806 INFORMATION SYSTEMS'),
                            (
                                b'080601',
                                b'080601 Aboriginal and Torres Strait Islander Information and Knowledge Systems',
                            ),
                            (b'080602', b'080602 Computer-Human Interaction'),
                            (b'080603', b'080603 Conceptual Modelling'),
                            (b'080604', b'080604 Database Management'),
                            (
                                b'080605',
                                b'080605 Decision Support and Group Support Systems',
                            ),
                            (b'080606', b'080606 Global Information Systems'),
                            (
                                b'080607',
                                b'080607 Information Engineering and Theory',
                            ),
                            (
                                b'080608',
                                b'080608 Information Systems Development Methodologies',
                            ),
                            (
                                b'080609',
                                b'080609 Information Systems Management',
                            ),
                            (
                                b'080610',
                                b'080610 Information Systems Organisation',
                            ),
                            (b'080611', b'080611 Information Systems Theory'),
                            (
                                b'080612',
                                b'080612 Interorganisational Information Systems and Web Services',
                            ),
                            (
                                b'080613',
                                b'080613 Maori Information and Knowledge Systems',
                            ),
                            (
                                b'080614',
                                b'080614 Pacific Peoples Information and Knowledge Systems',
                            ),
                            (
                                b'080699',
                                b'080699 Information Systems not elsewhere classified',
                            ),
                            (b'0807', b'0807 LIBRARY AND INFORMATION STUDIES'),
                            (
                                b'080701',
                                b'080701 Aboriginal and Torres Strait Islander Knowledge Management',
                            ),
                            (b'080702', b'080702 Health Informatics'),
                            (b'080703', b'080703 Human Information Behaviour'),
                            (
                                b'080704',
                                b'080704 Information Retrieval and Web Search',
                            ),
                            (b'080705', b'080705 Informetrics'),
                            (b'080706', b'080706 Librarianship'),
                            (
                                b'080707',
                                b'080707 Organisation of Information and Knowledge Resources',
                            ),
                            (
                                b'080708',
                                b'080708 Records and Information Management (excl. Business Records and Information Management)',
                            ),
                            (
                                b'080709',
                                b'080709 Social and Community Informatics',
                            ),
                            (
                                b'080799',
                                b'080799 Library and Information Studies not elsewhere classified',
                            ),
                            (
                                b'0899',
                                b'0899 OTHER INFORMATION AND COMPUTING SCIENCES',
                            ),
                            (
                                b'089999',
                                b'089999 Information and Computing Sciences not elsewhere classified',
                            ),
                            (b'09', b'09 ENGINEERING'),
                            (b'0901', b'0901 AEROSPACE ENGINEERING'),
                            (
                                b'090101',
                                b'090101 Aerodynamics (excl. Hypersonic Aerodynamics)',
                            ),
                            (b'090102', b'090102 Aerospace Materials'),
                            (b'090103', b'090103 Aerospace Structures'),
                            (
                                b'090104',
                                b'090104 Aircraft Performance and Flight Control Systems',
                            ),
                            (b'090105', b'090105 Avionics'),
                            (b'090106', b'090106 Flight Dynamics'),
                            (
                                b'090107',
                                b'090107 Hypersonic Propulsion and Hypersonic Aerodynamics',
                            ),
                            (
                                b'090108',
                                b'090108 Satellite, Space Vehicle and Missile Design and Testing',
                            ),
                            (
                                b'090199',
                                b'090199 Aerospace Engineering not elsewhere classified',
                            ),
                            (b'0902', b'0902 AUTOMOTIVE ENGINEERING'),
                            (
                                b'090201',
                                b'090201 Automotive Combustion and Fuel Engineering (incl. Alternative/Renewable Fuels)',
                            ),
                            (
                                b'090202',
                                b'090202 Automotive Engineering Materials',
                            ),
                            (b'090203', b'090203 Automotive Mechatronics'),
                            (
                                b'090204',
                                b'090204 Automotive Safety Engineering',
                            ),
                            (
                                b'090205',
                                b'090205 Hybrid Vehicles and Powertrains',
                            ),
                            (
                                b'090299',
                                b'090299 Automotive Engineering not elsewhere classified',
                            ),
                            (b'0903', b'0903 BIOMEDICAL ENGINEERING'),
                            (b'090301', b'090301 Biomaterials'),
                            (b'090302', b'090302 Biomechanical Engineering'),
                            (b'090303', b'090303 Biomedical Instrumentation'),
                            (b'090304', b'090304 Medical Devices'),
                            (b'090305', b'090305 Rehabilitation Engineering'),
                            (
                                b'090399',
                                b'090399 Biomedical Engineering not elsewhere classified',
                            ),
                            (b'0904', b'0904 CHEMICAL ENGINEERING'),
                            (
                                b'090401',
                                b'090401 Carbon Capture Engineering (excl. Sequestration)',
                            ),
                            (
                                b'090402',
                                b'090402 Catalytic Process Engineering',
                            ),
                            (b'090403', b'090403 Chemical Engineering Design'),
                            (
                                b'090404',
                                b'090404 Membrane and Separation Technologies',
                            ),
                            (
                                b'090405',
                                b'090405 Non-automotive Combustion and Fuel Engineering (incl. Alternative/Renewable Fuels)',
                            ),
                            (
                                b'090406',
                                b'090406 Powder and Particle Technology',
                            ),
                            (
                                b'090407',
                                b'090407 Process Control and Simulation',
                            ),
                            (b'090408', b'090408 Rheology'),
                            (
                                b'090409',
                                b'090409 Wastewater Treatment Processes',
                            ),
                            (b'090410', b'090410 Water Treatment Processes'),
                            (
                                b'090499',
                                b'090499 Chemical Engineering not elsewhere classified',
                            ),
                            (b'0905', b'0905 CIVIL ENGINEERING'),
                            (
                                b'090501',
                                b'090501 Civil Geotechnical Engineering',
                            ),
                            (b'090502', b'090502 Construction Engineering'),
                            (b'090503', b'090503 Construction Materials'),
                            (b'090504', b'090504 Earthquake Engineering'),
                            (
                                b'090505',
                                b'090505 Infrastructure Engineering and Asset Management',
                            ),
                            (b'090506', b'090506 Structural Engineering'),
                            (b'090507', b'090507 Transport Engineering'),
                            (b'090508', b'090508 Water Quality Engineering'),
                            (b'090509', b'090509 Water Resources Engineering'),
                            (
                                b'090599',
                                b'090599 Civil Engineering not elsewhere classified',
                            ),
                            (
                                b'0906',
                                b'0906 ELECTRICAL AND ELECTRONIC ENGINEERING',
                            ),
                            (b'090601', b'090601 Circuits and Systems'),
                            (
                                b'090602',
                                b'090602 Control Systems, Robotics and Automation',
                            ),
                            (b'090603', b'090603 Industrial Electronics'),
                            (
                                b'090604',
                                b'090604 Microelectronics and Integrated Circuits',
                            ),
                            (
                                b'090605',
                                b'090605 Photodetectors, Optical Sensors and Solar Cells',
                            ),
                            (
                                b'090606',
                                b'090606 Photonics and Electro-Optical Engineering (excl. Communications)',
                            ),
                            (
                                b'090607',
                                b'090607 Power and Energy Systems Engineering (excl. Renewable Power)',
                            ),
                            (
                                b'090608',
                                b'090608 Renewable Power and Energy Systems Engineering (excl. Solar Cells)',
                            ),
                            (b'090609', b'090609 Signal Processing'),
                            (
                                b'090699',
                                b'090699 Electrical and Electronic Engineering not elsewhere classified',
                            ),
                            (b'0907', b'0907 ENVIRONMENTAL ENGINEERING'),
                            (
                                b'090701',
                                b'090701 Environmental Engineering Design',
                            ),
                            (
                                b'090702',
                                b'090702 Environmental Engineering Modelling',
                            ),
                            (b'090703', b'090703 Environmental Technologies'),
                            (
                                b'090799',
                                b'090799 Environmental Engineering not elsewhere classified',
                            ),
                            (b'0908', b'0908 FOOD SCIENCES'),
                            (
                                b'090801',
                                b'090801 Food Chemistry and Molecular Gastronomy (excl. Wine)',
                            ),
                            (b'090802', b'090802 Food Engineering'),
                            (b'090803', b'090803 Food Nutritional Balance'),
                            (
                                b'090804',
                                b'090804 Food Packaging, Preservation and Safety',
                            ),
                            (b'090805', b'090805 Food Processing'),
                            (
                                b'090806',
                                b'090806 Wine Chemistry and Wine Sensory Science',
                            ),
                            (
                                b'090899',
                                b'090899 Food Sciences not elsewhere classified',
                            ),
                            (b'0909', b'0909 GEOMATIC ENGINEERING'),
                            (b'090901', b'090901 Cartography'),
                            (b'090902', b'090902 Geodesy'),
                            (
                                b'090903',
                                b'090903 Geospatial Information Systems',
                            ),
                            (
                                b'090904',
                                b'090904 Navigation and Position Fixing',
                            ),
                            (
                                b'090905',
                                b'090905 Photogrammetry and Remote Sensing',
                            ),
                            (
                                b'090906',
                                b'090906 Surveying (incl. Hydrographic Surveying)',
                            ),
                            (
                                b'090999',
                                b'090999 Geomatic Engineering not elsewhere classified',
                            ),
                            (b'0910', b'0910 MANUFACTURING ENGINEERING'),
                            (b'091001', b'091001 CAD/CAM Systems'),
                            (
                                b'091002',
                                b'091002 Flexible Manufacturing Systems',
                            ),
                            (b'091003', b'091003 Machine Tools'),
                            (b'091004', b'091004 Machining'),
                            (b'091005', b'091005 Manufacturing Management'),
                            (
                                b'091006',
                                b'091006 Manufacturing Processes and Technologies (excl. Textiles)',
                            ),
                            (
                                b'091007',
                                b'091007 Manufacturing Robotics and Mechatronics (excl. Automotive Mechatronics)',
                            ),
                            (
                                b'091008',
                                b'091008 Manufacturing Safety and Quality',
                            ),
                            (b'091009', b'091009 Microtechnology'),
                            (
                                b'091010',
                                b'091010 Packaging, Storage and Transportation (excl. Food and Agricultural Products)',
                            ),
                            (b'091011', b'091011 Precision Engineering'),
                            (b'091012', b'091012 Textile Technology'),
                            (
                                b'091099',
                                b'091099 Manufacturing Engineering not elsewhere classified',
                            ),
                            (b'0911', b'0911 MARITIME ENGINEERING'),
                            (b'091101', b'091101 Marine Engineering'),
                            (b'091102', b'091102 Naval Architecture'),
                            (b'091103', b'091103 Ocean Engineering'),
                            (
                                b'091104',
                                b'091104 Ship and Platform Hydrodynamics',
                            ),
                            (
                                b'091105',
                                b'091105 Ship and Platform Structures',
                            ),
                            (b'091106', b'091106 Special Vehicles'),
                            (
                                b'091199',
                                b'091199 Maritime Engineering not elsewhere classified',
                            ),
                            (b'0912', b'0912 MATERIALS ENGINEERING'),
                            (b'091201', b'091201 Ceramics'),
                            (
                                b'091202',
                                b'091202 Composite and Hybrid Materials',
                            ),
                            (b'091203', b'091203 Compound Semiconductors'),
                            (b'091204', b'091204 Elemental Semiconductors'),
                            (b'091205', b'091205 Functional Materials'),
                            (b'091206', b'091206 Glass'),
                            (b'091207', b'091207 Metals and Alloy Materials'),
                            (b'091208', b'091208 Organic Semiconductors'),
                            (b'091209', b'091209 Polymers and Plastics'),
                            (b'091210', b'091210 Timber, Pulp and Paper'),
                            (
                                b'091299',
                                b'091299 Materials Engineering not elsewhere classified',
                            ),
                            (b'0913', b'0913 MECHANICAL ENGINEERING'),
                            (
                                b'091301',
                                b'091301 Acoustics and Noise Control (excl. Architectural Acoustics)',
                            ),
                            (
                                b'091302',
                                b'091302 Automation and Control Engineering',
                            ),
                            (b'091303', b'091303 Autonomous Vehicles'),
                            (
                                b'091304',
                                b'091304 Dynamics, Vibration and Vibration Control',
                            ),
                            (
                                b'091305',
                                b'091305 Energy Generation, Conversion and Storage Engineering',
                            ),
                            (
                                b'091306',
                                b'091306 Microelectromechanical Systems (MEMS)',
                            ),
                            (
                                b'091307',
                                b'091307 Numerical Modelling and Mechanical Characterisation',
                            ),
                            (b'091308', b'091308 Solid Mechanics'),
                            (b'091309', b'091309 Tribology'),
                            (
                                b'091399',
                                b'091399 Mechanical Engineering not elsewhere classified',
                            ),
                            (
                                b'0914',
                                b'0914 RESOURCES ENGINEERING AND EXTRACTIVE METALLURGY',
                            ),
                            (b'091401', b'091401 Electrometallurgy'),
                            (
                                b'091402',
                                b'091402 Geomechanics and Resources Geotechnical Engineering',
                            ),
                            (b'091403', b'091403 Hydrometallurgy'),
                            (
                                b'091404',
                                b'091404 Mineral Processing/Beneficiation',
                            ),
                            (b'091405', b'091405 Mining Engineering'),
                            (
                                b'091406',
                                b'091406 Petroleum and Reservoir Engineering',
                            ),
                            (b'091407', b'091407 Pyrometallurgy'),
                            (
                                b'091499',
                                b'091499 Resources Engineering and Extractive Metallurgy not elsewhere classified',
                            ),
                            (b'0915', b'0915 INTERDISCIPLINARY ENGINEERING'),
                            (
                                b'091501',
                                b'091501 Computational Fluid Dynamics',
                            ),
                            (b'091502', b'091502 Computational Heat Transfer'),
                            (b'091503', b'091503 Engineering Practice'),
                            (
                                b'091504',
                                b'091504 Fluidisation and Fluid Mechanics',
                            ),
                            (
                                b'091505',
                                b'091505 Heat and Mass Transfer Operations',
                            ),
                            (
                                b'091506',
                                b'091506 Nuclear Engineering (incl. Fuel Enrichment and Waste Processing and Storage)',
                            ),
                            (
                                b'091507',
                                b'091507 Risk Engineering (excl. Earthquake Engineering)',
                            ),
                            (b'091508', b'091508 Turbulent Flows'),
                            (
                                b'091599',
                                b'091599 Interdisciplinary Engineering not elsewhere classified',
                            ),
                            (b'0999', b'0999 OTHER ENGINEERING'),
                            (b'099901', b'099901 Agricultural Engineering'),
                            (b'099902', b'099902 Engineering Instrumentation'),
                            (
                                b'099999',
                                b'099999 Engineering not elsewhere classified',
                            ),
                            (b'10', b'10 TECHNOLOGY'),
                            (b'1001', b'1001 AGRICULTURAL BIOTECHNOLOGY'),
                            (
                                b'100101',
                                b'100101 Agricultural Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100102',
                                b'100102 Agricultural Marine Biotechnology',
                            ),
                            (
                                b'100103',
                                b'100103 Agricultural Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100104',
                                b'100104 Genetically Modified Animals',
                            ),
                            (
                                b'100105',
                                b'100105 Genetically Modified Field Crops and Pasture',
                            ),
                            (
                                b'100106',
                                b'100106 Genetically Modified Horticulture Plants',
                            ),
                            (b'100107', b'100107 Genetically Modified Trees'),
                            (b'100108', b'100108 Livestock Cloning'),
                            (b'100109', b'100109 Transgenesis'),
                            (
                                b'100199',
                                b'100199 Agricultural Biotechnology not elsewhere classified',
                            ),
                            (b'1002', b'1002 ENVIRONMENTAL BIOTECHNOLOGY'),
                            (b'100201', b'100201 Biodiscovery'),
                            (b'100202', b'100202 Biological Control'),
                            (b'100203', b'100203 Bioremediation'),
                            (
                                b'100204',
                                b'100204 Environmental Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100205',
                                b'100205 Environmental Marine Biotechnology',
                            ),
                            (
                                b'100206',
                                b'100206 Environmental Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100299',
                                b'100299 Environmental Biotechnology not elsewhere classified',
                            ),
                            (b'1003', b'1003 INDUSTRIAL BIOTECHNOLOGY'),
                            (
                                b'100301',
                                b'100301 Biocatalysis and Enzyme Technology',
                            ),
                            (
                                b'100302',
                                b'100302 Bioprocessing, Bioproduction and Bioproducts',
                            ),
                            (b'100303', b'100303 Fermentation'),
                            (
                                b'100304',
                                b'100304 Industrial Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100305',
                                b'100305 Industrial Microbiology (incl. Biofeedstocks)',
                            ),
                            (
                                b'100306',
                                b'100306 Industrial Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100399',
                                b'100399 Industrial Biotechnology not elsewhere classified',
                            ),
                            (b'1004', b'1004 MEDICAL BIOTECHNOLOGY'),
                            (b'100401', b'100401 Gene and Molecular Therapy'),
                            (
                                b'100402',
                                b'100402 Medical Biotechnology Diagnostics (incl. Biosensors)',
                            ),
                            (
                                b'100403',
                                b'100403 Medical Molecular Engineering of Nucleic Acids and Proteins',
                            ),
                            (
                                b'100404',
                                b'100404 Regenerative Medicine (incl. Stem Cells and Tissue Engineering)',
                            ),
                            (
                                b'100499',
                                b'100499 Medical Biotechnology not elsewhere classified',
                            ),
                            (b'1005', b'1005 COMMUNICATIONS TECHNOLOGIES'),
                            (b'100501', b'100501 Antennas and Propagation'),
                            (
                                b'100502',
                                b'100502 Broadband and Modem Technology',
                            ),
                            (
                                b'100503',
                                b'100503 Computer Communications Networks',
                            ),
                            (b'100504', b'100504 Data Communications'),
                            (
                                b'100505',
                                b'100505 Microwave and Millimetrewave Theory and Technology',
                            ),
                            (
                                b'100506',
                                b'100506 Optical Fibre Communications',
                            ),
                            (
                                b'100507',
                                b'100507 Optical Networks and Systems',
                            ),
                            (b'100508', b'100508 Satellite Communications'),
                            (b'100509', b'100509 Video Communications'),
                            (b'100510', b'100510 Wireless Communications'),
                            (
                                b'100599',
                                b'100599 Communications Technologies not elsewhere classified',
                            ),
                            (b'1006', b'1006 COMPUTER HARDWARE'),
                            (
                                b'100601',
                                b'100601 Arithmetic and Logic Structures',
                            ),
                            (
                                b'100602',
                                b'100602 Input, Output and Data Devices',
                            ),
                            (b'100603', b'100603 Logic Design'),
                            (b'100604', b'100604 Memory Structures'),
                            (
                                b'100605',
                                b'100605 Performance Evaluation; Testing and Simulation of Reliability',
                            ),
                            (b'100606', b'100606 Processor Architectures'),
                            (
                                b'100699',
                                b'100699 Computer Hardware not elsewhere classified',
                            ),
                            (b'1007', b'1007 NANOTECHNOLOGY'),
                            (
                                b'100701',
                                b'100701 Environmental Nanotechnology',
                            ),
                            (
                                b'100702',
                                b'100702 Molecular and Organic Electronics',
                            ),
                            (b'100703', b'100703 Nanobiotechnology'),
                            (
                                b'100704',
                                b'100704 Nanoelectromechanical Systems',
                            ),
                            (b'100705', b'100705 Nanoelectronics'),
                            (
                                b'100706',
                                b'100706 Nanofabrication, Growth and Self Assembly',
                            ),
                            (b'100707', b'100707 Nanomanufacturing'),
                            (b'100708', b'100708 Nanomaterials'),
                            (b'100709', b'100709 Nanomedicine'),
                            (b'100710', b'100710 Nanometrology'),
                            (b'100711', b'100711 Nanophotonics'),
                            (b'100712', b'100712 Nanoscale Characterisation'),
                            (
                                b'100713',
                                b'100713 Nanotoxicology, Health and Safety',
                            ),
                            (
                                b'100799',
                                b'100799 Nanotechnology not elsewhere classified',
                            ),
                            (b'1099', b'1099 OTHER TECHNOLOGY'),
                            (
                                b'109999',
                                b'109999 Technology not elsewhere classified',
                            ),
                            (b'11', b'11 MEDICAL AND HEALTH SCIENCES'),
                            (
                                b'1101',
                                b'1101 MEDICAL BIOCHEMISTRY AND METABOLOMICS',
                            ),
                            (
                                b'110101',
                                b'110101 Medical Biochemistry: Amino Acids and Metabolites',
                            ),
                            (
                                b'110102',
                                b'110102 Medical Biochemistry: Carbohydrates',
                            ),
                            (
                                b'110103',
                                b'110103 Medical Biochemistry: Inorganic Elements and Compounds',
                            ),
                            (
                                b'110104',
                                b'110104 Medical Biochemistry: Lipids',
                            ),
                            (
                                b'110105',
                                b'110105 Medical Biochemistry: Nucleic Acids',
                            ),
                            (
                                b'110106',
                                b'110106 Medical Biochemistry: Proteins and Peptides (incl. Medical Proteomics)',
                            ),
                            (b'110107', b'110107 Metabolic Medicine'),
                            (
                                b'110199',
                                b'110199 Medical Biochemistry and Metabolomics not elsewhere classified',
                            ),
                            (
                                b'1102',
                                b'1102 CARDIORESPIRATORY MEDICINE AND HAEMATOLOGY',
                            ),
                            (
                                b'110201',
                                b'110201 Cardiology (incl. Cardiovascular Diseases)',
                            ),
                            (b'110202', b'110202 Haematology'),
                            (b'110203', b'110203 Respiratory Diseases'),
                            (
                                b'110299',
                                b'110299 Cardiorespiratory Medicine and Haematology not elsewhere classified',
                            ),
                            (b'1103', b'1103 CLINICAL SCIENCES'),
                            (b'110301', b'110301 Anaesthesiology'),
                            (
                                b'110302',
                                b'110302 Clinical Chemistry (diagnostics)',
                            ),
                            (b'110303', b'110303 Clinical Microbiology'),
                            (b'110304', b'110304 Dermatology'),
                            (b'110305', b'110305 Emergency Medicine'),
                            (b'110306', b'110306 Endocrinology'),
                            (
                                b'110307',
                                b'110307 Gastroenterology and Hepatology',
                            ),
                            (b'110308', b'110308 Geriatrics and Gerontology'),
                            (b'110309', b'110309 Infectious Diseases'),
                            (b'110310', b'110310 Intensive Care'),
                            (
                                b'110311',
                                b'110311 Medical Genetics (excl. Cancer Genetics)',
                            ),
                            (b'110312', b'110312 Nephrology and Urology'),
                            (b'110313', b'110313 Nuclear Medicine'),
                            (b'110314', b'110314 Orthopaedics'),
                            (b'110315', b'110315 Otorhinolaryngology'),
                            (
                                b'110316',
                                b'110316 Pathology (excl. Oral Pathology)',
                            ),
                            (b'110317', b'110317 Physiotherapy'),
                            (b'110318', b'110318 Podiatry'),
                            (
                                b'110319',
                                b'110319 Psychiatry (incl. Psychotherapy)',
                            ),
                            (b'110320', b'110320 Radiology and Organ Imaging'),
                            (
                                b'110321',
                                b'110321 Rehabilitation and Therapy (excl. Physiotherapy)',
                            ),
                            (b'110322', b'110322 Rheumatology and Arthritis'),
                            (b'110323', b'110323 Surgery'),
                            (b'110324', b'110324 Venereology'),
                            (
                                b'110399',
                                b'110399 Clinical Sciences not elsewhere classified',
                            ),
                            (
                                b'1104',
                                b'1104 COMPLEMENTARY AND ALTERNATIVE MEDICINE',
                            ),
                            (b'110401', b'110401 Chiropractic'),
                            (b'110402', b'110402 Naturopathy'),
                            (
                                b'110403',
                                b'110403 Traditional Aboriginal and Torres Strait Islander Medicine and Treatments',
                            ),
                            (
                                b'110404',
                                b'110404 Traditional Chinese Medicine and Treatments',
                            ),
                            (
                                b'110405',
                                b'110405 Traditional Maori Medicine and Treatments',
                            ),
                            (
                                b'110499',
                                b'110499 Complementary and Alternative Medicine not elsewhere classified',
                            ),
                            (b'1105', b'1105 DENTISTRY'),
                            (
                                b'110501',
                                b'110501 Dental Materials and Equipment',
                            ),
                            (
                                b'110502',
                                b'110502 Dental Therapeutics, Pharmacology and Toxicology',
                            ),
                            (b'110503', b'110503 Endodontics'),
                            (
                                b'110504',
                                b'110504 Oral and Maxillofacial Surgery',
                            ),
                            (b'110505', b'110505 Oral Medicine and Pathology'),
                            (
                                b'110506',
                                b'110506 Orthodontics and Dentofacial Orthopaedics',
                            ),
                            (b'110507', b'110507 Paedodontics'),
                            (b'110508', b'110508 Periodontics'),
                            (b'110509', b'110509 Special Needs Dentistry'),
                            (
                                b'110599',
                                b'110599 Dentistry not elsewhere classified',
                            ),
                            (
                                b'1106',
                                b'1106 HUMAN MOVEMENT AND SPORTS SCIENCE',
                            ),
                            (b'110601', b'110601 Biomechanics'),
                            (b'110602', b'110602 Exercise Physiology'),
                            (b'110603', b'110603 Motor Control'),
                            (b'110604', b'110604 Sports Medicine'),
                            (
                                b'110699',
                                b'110699 Human Movement and Sports Science not elsewhere classified',
                            ),
                            (b'1107', b'1107 IMMUNOLOGY'),
                            (b'110701', b'110701 Allergy'),
                            (
                                b'110702',
                                b'110702 Applied Immunology (incl. Antibody Engineering, Xenotransplantation and T-cell Therapies)',
                            ),
                            (b'110703', b'110703 Autoimmunity'),
                            (b'110704', b'110704 Cellular Immunology'),
                            (
                                b'110705',
                                b'110705 Humoural Immunology and Immunochemistry',
                            ),
                            (
                                b'110706',
                                b'110706 Immunogenetics (incl. Genetic Immunology)',
                            ),
                            (b'110707', b'110707 Innate Immunity'),
                            (b'110708', b'110708 Transplantation Immunology'),
                            (b'110709', b'110709 Tumour Immunology'),
                            (
                                b'110799',
                                b'110799 Immunology not elsewhere classified',
                            ),
                            (b'1108', b'1108 MEDICAL MICROBIOLOGY'),
                            (b'110801', b'110801 Medical Bacteriology'),
                            (
                                b'110802',
                                b'110802 Medical Infection Agents (incl. Prions)',
                            ),
                            (b'110803', b'110803 Medical Parasitology'),
                            (b'110804', b'110804 Medical Virology'),
                            (
                                b'110899',
                                b'110899 Medical Microbiology not elsewhere classified',
                            ),
                            (b'1109', b'1109 NEUROSCIENCES'),
                            (b'110901', b'110901 Autonomic Nervous System'),
                            (b'110902', b'110902 Cellular Nervous System'),
                            (b'110903', b'110903 Central Nervous System'),
                            (
                                b'110904',
                                b'110904 Neurology and Neuromuscular Diseases',
                            ),
                            (b'110905', b'110905 Peripheral Nervous System'),
                            (b'110906', b'110906 Sensory Systems'),
                            (
                                b'110999',
                                b'110999 Neurosciences not elsewhere classified',
                            ),
                            (b'1110', b'1110 NURSING'),
                            (b'111001', b'111001 Aged Care Nursing'),
                            (
                                b'111002',
                                b'111002 Clinical Nursing: Primary (Preventative)',
                            ),
                            (
                                b'111003',
                                b'111003 Clinical Nursing: Secondary (Acute Care)',
                            ),
                            (
                                b'111004',
                                b'111004 Clinical Nursing: Tertiary (Rehabilitative)',
                            ),
                            (b'111005', b'111005 Mental Health Nursing'),
                            (b'111006', b'111006 Midwifery'),
                            (
                                b'111099',
                                b'111099 Nursing not elsewhere classified',
                            ),
                            (b'1111', b'1111 NUTRITION AND DIETETICS'),
                            (
                                b'111101',
                                b'111101 Clinical and Sports Nutrition',
                            ),
                            (b'111102', b'111102 Dietetics and Nutrigenomics'),
                            (b'111103', b'111103 Nutritional Physiology'),
                            (
                                b'111104',
                                b'111104 Public Nutrition Intervention',
                            ),
                            (
                                b'111199',
                                b'111199 Nutrition and Dietetics not elsewhere classified',
                            ),
                            (b'1112', b'1112 ONCOLOGY AND CARCINOGENESIS'),
                            (b'111201', b'111201 Cancer Cell Biology'),
                            (b'111202', b'111202 Cancer Diagnosis'),
                            (b'111203', b'111203 Cancer Genetics'),
                            (
                                b'111204',
                                b'111204 Cancer Therapy (excl. Chemotherapy and Radiation Therapy)',
                            ),
                            (b'111205', b'111205 Chemotherapy'),
                            (b'111206', b'111206 Haematological Tumours'),
                            (b'111207', b'111207 Molecular Targets'),
                            (b'111208', b'111208 Radiation Therapy'),
                            (b'111209', b'111209 Solid Tumours'),
                            (
                                b'111299',
                                b'111299 Oncology and Carcinogenesis not elsewhere classified',
                            ),
                            (b'1113', b'1113 OPHTHALMOLOGY AND OPTOMETRY'),
                            (b'111301', b'111301 Ophthalmology'),
                            (b'111302', b'111302 Optical Technology'),
                            (b'111303', b'111303 Vision Science'),
                            (
                                b'111399',
                                b'111399 Ophthalmology and Optometry not elsewhere classified',
                            ),
                            (
                                b'1114',
                                b'1114 PAEDIATRICS AND REPRODUCTIVE MEDICINE',
                            ),
                            (
                                b'111401',
                                b'111401 Foetal Development and Medicine',
                            ),
                            (b'111402', b'111402 Obstetrics and Gynaecology'),
                            (b'111403', b'111403 Paediatrics'),
                            (b'111404', b'111404 Reproduction'),
                            (
                                b'111499',
                                b'111499 Paediatrics and Reproductive Medicine not elsewhere classified',
                            ),
                            (
                                b'1115',
                                b'1115 PHARMACOLOGY AND PHARMACEUTICAL SCIENCES',
                            ),
                            (b'111501', b'111501 Basic Pharmacology'),
                            (
                                b'111502',
                                b'111502 Clinical Pharmacology and Therapeutics',
                            ),
                            (
                                b'111503',
                                b'111503 Clinical Pharmacy and Pharmacy Practice',
                            ),
                            (b'111504', b'111504 Pharmaceutical Sciences'),
                            (b'111505', b'111505 Pharmacogenomics'),
                            (
                                b'111506',
                                b'111506 Toxicology (incl. Clinical Toxicology)',
                            ),
                            (
                                b'111599',
                                b'111599 Pharmacology and Pharmaceutical Sciences not elsewhere classified',
                            ),
                            (b'1116', b'1116 MEDICAL PHYSIOLOGY'),
                            (b'111601', b'111601 Cell Physiology'),
                            (b'111602', b'111602 Human Biophysics'),
                            (b'111603', b'111603 Systems Physiology'),
                            (
                                b'111699',
                                b'111699 Medical Physiology not elsewhere classified',
                            ),
                            (
                                b'1117',
                                b'1117 PUBLIC HEALTH AND HEALTH SERVICES',
                            ),
                            (
                                b'111701',
                                b'111701 Aboriginal and Torres Strait Islander Health',
                            ),
                            (b'111702', b'111702 Aged Health Care'),
                            (b'111703', b'111703 Care for Disabled'),
                            (b'111704', b'111704 Community Child Health'),
                            (
                                b'111705',
                                b'111705 Environmental and Occupational Health and Safety',
                            ),
                            (b'111706', b'111706 Epidemiology'),
                            (b'111707', b'111707 Family Care'),
                            (
                                b'111708',
                                b'111708 Health and Community Services',
                            ),
                            (b'111709', b'111709 Health Care Administration'),
                            (b'111710', b'111710 Health Counselling'),
                            (
                                b'111711',
                                b'111711 Health Information Systems (incl. Surveillance)',
                            ),
                            (b'111712', b'111712 Health Promotion'),
                            (b'111713', b'111713 Maori Health'),
                            (b'111714', b'111714 Mental Health'),
                            (b'111715', b'111715 Pacific Peoples Health'),
                            (b'111716', b'111716 Preventive Medicine'),
                            (b'111717', b'111717 Primary Health Care'),
                            (b'111718', b'111718 Residential Client Care'),
                            (
                                b'111799',
                                b'111799 Public Health and Health Services not elsewhere classified',
                            ),
                            (
                                b'1199',
                                b'1199 OTHER MEDICAL AND HEALTH SCIENCES',
                            ),
                            (
                                b'119999',
                                b'119999 Medical and Health Sciences not elsewhere classified',
                            ),
                            (b'12', b'12 BUILT ENVIRONMENT AND DESIGN'),
                            (b'1201', b'1201 ARCHITECTURE'),
                            (b'120101', b'120101 Architectural Design'),
                            (
                                b'120102',
                                b'120102 Architectural Heritage and Conservation',
                            ),
                            (
                                b'120103',
                                b'120103 Architectural History and Theory',
                            ),
                            (
                                b'120104',
                                b'120104 Architectural Science and Technology (incl. Acoustics, Lighting, Structure and Ecologically Sustainable Design)',
                            ),
                            (b'120105', b'120105 Architecture Management'),
                            (b'120106', b'120106 Interior Design'),
                            (b'120107', b'120107 Landscape Architecture'),
                            (
                                b'120199',
                                b'120199 Architecture not elsewhere classified',
                            ),
                            (b'1202', b'1202 BUILDING'),
                            (
                                b'120201',
                                b'120201 Building Construction Management and Project Planning',
                            ),
                            (
                                b'120202',
                                b'120202 Building Science and Techniques',
                            ),
                            (b'120203', b'120203 Quantity Surveying'),
                            (
                                b'120299',
                                b'120299 Building not elsewhere classified',
                            ),
                            (b'1203', b'1203 DESIGN PRACTICE AND MANAGEMENT'),
                            (b'120301', b'120301 Design History and Theory'),
                            (b'120302', b'120302 Design Innovation'),
                            (
                                b'120303',
                                b'120303 Design Management and Studio and Professional Practice',
                            ),
                            (
                                b'120304',
                                b'120304 Digital and Interaction Design',
                            ),
                            (b'120305', b'120305 Industrial Design'),
                            (b'120306', b'120306 Textile and Fashion Design'),
                            (
                                b'120307',
                                b'120307 Visual Communication Design (incl. Graphic Design)',
                            ),
                            (
                                b'120399',
                                b'120399 Design Practice and Management not elsewhere classified',
                            ),
                            (b'1204', b'1204 ENGINEERING DESIGN'),
                            (
                                b'120401',
                                b'120401 Engineering Design Empirical Studies',
                            ),
                            (
                                b'120402',
                                b'120402 Engineering Design Knowledge',
                            ),
                            (b'120403', b'120403 Engineering Design Methods'),
                            (b'120404', b'120404 Engineering Systems Design'),
                            (
                                b'120405',
                                b'120405 Models of Engineering Design',
                            ),
                            (
                                b'120499',
                                b'120499 Engineering Design not elsewhere classified',
                            ),
                            (b'1205', b'1205 URBAN AND REGIONAL PLANNING'),
                            (b'120501', b'120501 Community Planning'),
                            (
                                b'120502',
                                b'120502 History and Theory of the Built Environment (excl. Architecture)',
                            ),
                            (
                                b'120503',
                                b'120503 Housing Markets, Development, Management',
                            ),
                            (
                                b'120504',
                                b'120504 Land Use and Environmental Planning',
                            ),
                            (
                                b'120505',
                                b'120505 Regional Analysis and Development',
                            ),
                            (b'120506', b'120506 Transport Planning'),
                            (
                                b'120507',
                                b'120507 Urban Analysis and Development',
                            ),
                            (b'120508', b'120508 Urban Design'),
                            (
                                b'120599',
                                b'120599 Urban and Regional Planning not elsewhere classified',
                            ),
                            (
                                b'1299',
                                b'1299 OTHER BUILT ENVIRONMENT AND DESIGN',
                            ),
                            (
                                b'129999',
                                b'129999 Built Environment and Design not elsewhere classified',
                            ),
                            (b'13', b'13 EDUCATION'),
                            (b'1301', b'1301 EDUCATION SYSTEMS'),
                            (
                                b'130101',
                                b'130101 Continuing and Community Education',
                            ),
                            (
                                b'130102',
                                b'130102 Early Childhood Education (excl. Maori)',
                            ),
                            (b'130103', b'130103 Higher Education'),
                            (
                                b'130104',
                                b'130104 Kura Kaupapa Maori (Maori Primary Education)',
                            ),
                            (
                                b'130105',
                                b'130105 Primary Education (excl. Maori)',
                            ),
                            (b'130106', b'130106 Secondary Education'),
                            (
                                b'130107',
                                b'130107 Te Whariki (Maori Early Childhood Education)',
                            ),
                            (
                                b'130108',
                                b'130108 Technical, Further and Workplace Education',
                            ),
                            (
                                b'130199',
                                b'130199 Education systems not elsewhere classified',
                            ),
                            (b'1302', b'1302 CURRICULUM AND PEDAGOGY'),
                            (
                                b'130201',
                                b'130201 Creative Arts, Media and Communication Curriculum and Pedagogy',
                            ),
                            (
                                b'130202',
                                b'130202 Curriculum and Pedagogy Theory and Development',
                            ),
                            (
                                b'130203',
                                b'130203 Economics, Business and Management Curriculum and Pedagogy',
                            ),
                            (
                                b'130204',
                                b'130204 English and Literacy Curriculum and Pedagogy (excl. LOTE, ESL and TESOL)',
                            ),
                            (
                                b'130205',
                                b'130205 Humanities and Social Sciences Curriculum and Pedagogy (excl. Economics, Business and Management)',
                            ),
                            (
                                b'130206',
                                b'130206 Kohanga Reo (Maori Language Curriculum and Pedagogy)',
                            ),
                            (
                                b'130207',
                                b'130207 LOTE, ESL and TESOL Curriculum and Pedagogy (excl. Maori)',
                            ),
                            (
                                b'130208',
                                b'130208 Mathematics and Numeracy Curriculum and Pedagogy',
                            ),
                            (
                                b'130209',
                                b'130209 Medicine, Nursing and Health Curriculum and Pedagogy',
                            ),
                            (
                                b'130210',
                                b'130210 Physical Education and Development Curriculum and Pedagogy',
                            ),
                            (
                                b'130211',
                                b'130211 Religion Curriculum and Pedagogy',
                            ),
                            (
                                b'130212',
                                b'130212 Science, Technology and Engineering Curriculum and Pedagogy',
                            ),
                            (
                                b'130213',
                                b'130213 Vocational Education and Training Curriculum and Pedagogy',
                            ),
                            (
                                b'130299',
                                b'130299 Curriculum and Pedagogy not elsewhere classified',
                            ),
                            (b'1303', b'1303 SPECIALIST STUDIES IN EDUCATION'),
                            (
                                b'130301',
                                b'130301 Aboriginal and Torres Strait Islander Education',
                            ),
                            (
                                b'130302',
                                b'130302 Comparative and Cross-Cultural Education',
                            ),
                            (
                                b'130303',
                                b'130303 Education Assessment and Evaluation',
                            ),
                            (
                                b'130304',
                                b'130304 Educational Administration, Management and Leadership',
                            ),
                            (b'130305', b'130305 Educational Counselling'),
                            (
                                b'130306',
                                b'130306 Educational Technology and Computing',
                            ),
                            (
                                b'130307',
                                b'130307 Ethnic Education (excl. Aboriginal and Torres Strait Islander, Maori and Pacific Peoples)',
                            ),
                            (
                                b'130308',
                                b'130308 Gender, Sexuality and Education',
                            ),
                            (b'130309', b'130309 Learning Sciences'),
                            (
                                b'130310',
                                b'130310 Maori Education (excl. Early Childhood and Primary Education)',
                            ),
                            (b'130311', b'130311 Pacific Peoples Education'),
                            (
                                b'130312',
                                b'130312 Special Education and Disability',
                            ),
                            (
                                b'130313',
                                b'130313 Teacher Education and Professional Development of Educators',
                            ),
                            (
                                b'130399',
                                b'130399 Specialist Studies in Education not elsewhere classified',
                            ),
                            (b'1399', b'1399 OTHER EDUCATION'),
                            (
                                b'139999',
                                b'139999 Education not elsewhere classified',
                            ),
                            (b'14', b'14 ECONOMICS'),
                            (b'1401', b'1401 ECONOMIC THEORY'),
                            (b'140101', b'140101 History of Economic Thought'),
                            (b'140102', b'140102 Macroeconomic Theory'),
                            (b'140103', b'140103 Mathematical Economics'),
                            (b'140104', b'140104 Microeconomic Theory'),
                            (
                                b'140199',
                                b'140199 Economic Theory not elsewhere classified',
                            ),
                            (b'1402', b'1402 APPLIED ECONOMICS'),
                            (b'140201', b'140201 Agricultural Economics'),
                            (
                                b'140202',
                                b'140202 Economic Development and Growth',
                            ),
                            (b'140203', b'140203 Economic History'),
                            (b'140204', b'140204 Economics of Education'),
                            (
                                b'140205',
                                b'140205 Environment and Resource Economics',
                            ),
                            (b'140206', b'140206 Experimental Economics'),
                            (b'140207', b'140207 Financial Economics'),
                            (b'140208', b'140208 Health Economics'),
                            (
                                b'140209',
                                b'140209 Industry Economics and Industrial Organisation',
                            ),
                            (
                                b'140210',
                                b'140210 International Economics and International Finance',
                            ),
                            (b'140211', b'140211 Labour Economics'),
                            (
                                b'140212',
                                b'140212 Macroeconomics (incl. Monetary and Fiscal Theory)',
                            ),
                            (
                                b'140213',
                                b'140213 Public Economics- Public Choice',
                            ),
                            (
                                b'140214',
                                b'140214 Public Economics- Publically Provided Goods',
                            ),
                            (
                                b'140215',
                                b'140215 Public Economics- Taxation and Revenue',
                            ),
                            (b'140216', b'140216 Tourism Economics'),
                            (b'140217', b'140217 Transport Economics'),
                            (
                                b'140218',
                                b'140218 Urban and Regional Economics',
                            ),
                            (b'140219', b'140219 Welfare Economics'),
                            (
                                b'140299',
                                b'140299 Applied Economics not elsewhere classified',
                            ),
                            (b'1403', b'1403 ECONOMETRICS'),
                            (b'140301', b'140301 Cross-Sectional Analysis'),
                            (
                                b'140302',
                                b'140302 Econometric and Statistical Methods',
                            ),
                            (
                                b'140303',
                                b'140303 Economic Models and Forecasting',
                            ),
                            (b'140304', b'140304 Panel Data Analysis'),
                            (b'140305', b'140305 Time-Series Analysis'),
                            (
                                b'140399',
                                b'140399 Econometrics not elsewhere classified',
                            ),
                            (b'1499', b'1499 OTHER ECONOMICS'),
                            (
                                b'149901',
                                b'149901 Comparative Economic Systems',
                            ),
                            (b'149902', b'149902 Ecological Economics'),
                            (b'149903', b'149903 Heterodox Economics'),
                            (
                                b'149999',
                                b'149999 Economics not elsewhere classified',
                            ),
                            (
                                b'15',
                                b'15 COMMERCE, MANAGEMENT, TOURISM AND SERVICES',
                            ),
                            (
                                b'1501',
                                b'1501 ACCOUNTING, AUDITING AND ACCOUNTABILITY',
                            ),
                            (
                                b'150101',
                                b'150101 Accounting Theory and Standards',
                            ),
                            (b'150102', b'150102 Auditing and Accountability'),
                            (b'150103', b'150103 Financial Accounting'),
                            (b'150104', b'150104 International Accounting'),
                            (b'150105', b'150105 Management Accounting'),
                            (
                                b'150106',
                                b'150106 Sustainability Accounting and Reporting',
                            ),
                            (b'150107', b'150107 Taxation Accounting'),
                            (
                                b'150199',
                                b'150199 Accounting, Auditing and Accountability not elsewhere classified',
                            ),
                            (b'1502', b'1502 BANKING, FINANCE AND INVESTMENT'),
                            (b'150201', b'150201 Finance'),
                            (b'150202', b'150202 Financial Econometrics'),
                            (
                                b'150203',
                                b'150203 Financial Institutions (incl. Banking)',
                            ),
                            (b'150204', b'150204 Insurance Studies'),
                            (
                                b'150205',
                                b'150205 Investment and Risk Management',
                            ),
                            (
                                b'150299',
                                b'150299 Banking, Finance and Investment not elsewhere classified',
                            ),
                            (b'1503', b'1503 BUSINESS AND MANAGEMENT'),
                            (
                                b'150301',
                                b'150301 Business Information Management (incl. Records, Knowledge and Information Management, and Intelligence)',
                            ),
                            (
                                b'150302',
                                b'150302 Business Information Systems',
                            ),
                            (
                                b'150303',
                                b'150303 Corporate Governance and Stakeholder Engagement',
                            ),
                            (b'150304', b'150304 Entrepreneurship'),
                            (b'150305', b'150305 Human Resources Management'),
                            (b'150306', b'150306 Industrial Relations'),
                            (
                                b'150307',
                                b'150307 Innovation and Technology Management',
                            ),
                            (b'150308', b'150308 International Business'),
                            (
                                b'150309',
                                b'150309 Logistics and Supply Chain Management',
                            ),
                            (
                                b'150310',
                                b'150310 Organisation and Management Theory',
                            ),
                            (b'150311', b'150311 Organisational Behaviour'),
                            (
                                b'150312',
                                b'150312 Organisational Planning and Management',
                            ),
                            (b'150313', b'150313 Quality Management'),
                            (b'150314', b'150314 Small Business Management'),
                            (
                                b'150399',
                                b'150399 Business and Management not elsewhere classified',
                            ),
                            (b'1504', b'1504 COMMERCIAL SERVICES'),
                            (
                                b'150401',
                                b'150401 Food and Hospitality Services',
                            ),
                            (b'150402', b'150402 Hospitality Management'),
                            (
                                b'150403',
                                b'150403 Real Estate and Valuation Services',
                            ),
                            (
                                b'150404',
                                b'150404 Sport and Leisure Management',
                            ),
                            (
                                b'150499',
                                b'150499 Commercial Services not elsewhere classified',
                            ),
                            (b'1505', b'1505 MARKETING'),
                            (
                                b'150501',
                                b'150501 Consumer-Oriented Product or Service Development',
                            ),
                            (b'150502', b'150502 Marketing Communications'),
                            (
                                b'150503',
                                b'150503 Marketing Management (incl. Strategy and Customer Relations)',
                            ),
                            (b'150504', b'150504 Marketing Measurement'),
                            (
                                b'150505',
                                b'150505 Marketing Research Methodology',
                            ),
                            (b'150506', b'150506 Marketing Theory'),
                            (
                                b'150507',
                                b'150507 Pricing (incl. Consumer Value Estimation)',
                            ),
                            (
                                b'150599',
                                b'150599 Marketing not elsewhere classified',
                            ),
                            (b'1506', b'1506 TOURISM'),
                            (b'150601', b'150601 Impacts of Tourism'),
                            (b'150602', b'150602 Tourism Forecasting'),
                            (b'150603', b'150603 Tourism Management'),
                            (b'150604', b'150604 Tourism Marketing'),
                            (b'150605', b'150605 Tourism Resource Appraisal'),
                            (
                                b'150606',
                                b'150606 Tourist Behaviour and Visitor Experience',
                            ),
                            (
                                b'150699',
                                b'150699 Tourism not elsewhere classified',
                            ),
                            (
                                b'1507',
                                b'1507 TRANSPORTATION AND FREIGHT SERVICES',
                            ),
                            (
                                b'150701',
                                b'150701 Air Transportation and Freight Services',
                            ),
                            (
                                b'150702',
                                b'150702 Rail Transportation and Freight Services',
                            ),
                            (
                                b'150703',
                                b'150703 Road Transportation and Freight Services',
                            ),
                            (
                                b'150799',
                                b'150799 Transportation and Freight Services not elsewhere classified',
                            ),
                            (
                                b'1599',
                                b'1599 OTHER COMMERCE, MANAGEMENT, TOURISM AND SERVICES',
                            ),
                            (
                                b'159999',
                                b'159999 Commerce, Management, Tourism and Services not elsewhere classified',
                            ),
                            (b'16', b'16 STUDIES IN HUMAN SOCIETY'),
                            (b'1601', b'1601 ANTHROPOLOGY'),
                            (b'160101', b'160101 Anthropology of Development'),
                            (
                                b'160102',
                                b'160102 Biological (Physical) Anthropology',
                            ),
                            (b'160103', b'160103 Linguistic Anthropology'),
                            (
                                b'160104',
                                b'160104 Social and Cultural Anthropology',
                            ),
                            (
                                b'160199',
                                b'160199 Anthropology not elsewhere classified',
                            ),
                            (b'1602', b'1602 CRIMINOLOGY'),
                            (
                                b'160201',
                                b'160201 Causes and Prevention of Crime',
                            ),
                            (
                                b'160202',
                                b'160202 Correctional Theory, Offender Treatment and Rehabilitation',
                            ),
                            (b'160203', b'160203 Courts and Sentencing'),
                            (b'160204', b'160204 Criminological Theories'),
                            (
                                b'160205',
                                b'160205 Police Administration, Procedures and Practice',
                            ),
                            (
                                b'160206',
                                b'160206 Private Policing and Security Services',
                            ),
                            (
                                b'160299',
                                b'160299 Criminology not elsewhere classified',
                            ),
                            (b'1603', b'1603 DEMOGRAPHY'),
                            (
                                b'160301',
                                b'160301 Family and Household Studies',
                            ),
                            (b'160302', b'160302 Fertility'),
                            (b'160303', b'160303 Migration'),
                            (b'160304', b'160304 Mortality'),
                            (
                                b'160305',
                                b'160305 Population Trends and Policies',
                            ),
                            (
                                b'160399',
                                b'160399 Demography not elsewhere classified',
                            ),
                            (b'1604', b'1604 HUMAN GEOGRAPHY'),
                            (b'160401', b'160401 Economic Geography'),
                            (
                                b'160402',
                                b'160402 Recreation, Leisure and Tourism Geography',
                            ),
                            (
                                b'160403',
                                b'160403 Social and Cultural Geography',
                            ),
                            (
                                b'160404',
                                b'160404 Urban and Regional Studies (excl. Planning)',
                            ),
                            (
                                b'160499',
                                b'160499 Human Geography not elsewhere classified',
                            ),
                            (b'1605', b'1605 POLICY AND ADMINISTRATION'),
                            (
                                b'160501',
                                b'160501 Aboriginal and Torres Strait Islander Policy',
                            ),
                            (b'160502', b'160502 Arts and Cultural Policy'),
                            (
                                b'160503',
                                b'160503 Communications and Media Policy',
                            ),
                            (b'160504', b'160504 Crime Policy'),
                            (b'160505', b'160505 Economic Development Policy'),
                            (b'160506', b'160506 Education Policy'),
                            (b'160507', b'160507 Environment Policy'),
                            (b'160508', b'160508 Health Policy'),
                            (b'160509', b'160509 Public Administration'),
                            (b'160510', b'160510 Public Policy'),
                            (
                                b'160511',
                                b'160511 Research, Science and Technology Policy',
                            ),
                            (b'160512', b'160512 Social Policy'),
                            (b'160513', b'160513 Tourism Policy'),
                            (b'160514', b'160514 Urban Policy'),
                            (
                                b'160599',
                                b'160599 Policy and Administration not elsewhere classified',
                            ),
                            (b'1606', b'1606 POLITICAL SCIENCE'),
                            (
                                b'160601',
                                b'160601 Australian Government and Politics',
                            ),
                            (b'160602', b'160602 Citizenship'),
                            (
                                b'160603',
                                b'160603 Comparative Government and Politics',
                            ),
                            (b'160604', b'160604 Defence Studies'),
                            (b'160605', b'160605 Environmental Politics'),
                            (
                                b'160606',
                                b'160606 Government and Politics of Asia and the Pacific',
                            ),
                            (b'160607', b'160607 International Relations'),
                            (
                                b'160608',
                                b'160608 New Zealand Government and Politics',
                            ),
                            (
                                b'160609',
                                b'160609 Political Theory and Political Philosophy',
                            ),
                            (
                                b'160699',
                                b'160699 Political Science not elsewhere classified',
                            ),
                            (b'1607', b'1607 SOCIAL WORK'),
                            (
                                b'160701',
                                b'160701 Clinical Social Work Practice',
                            ),
                            (
                                b'160702',
                                b'160702 Counselling, Welfare and Community Services',
                            ),
                            (b'160703', b'160703 Social Program Evaluation'),
                            (
                                b'160799',
                                b'160799 Social Work not elsewhere classified',
                            ),
                            (b'1608', b'1608 SOCIOLOGY'),
                            (
                                b'160801',
                                b'160801 Applied Sociology, Program Evaluation and Social Impact Assessment',
                            ),
                            (b'160802', b'160802 Environmental Sociology'),
                            (b'160803', b'160803 Race and Ethnic Relations'),
                            (b'160804', b'160804 Rural Sociology'),
                            (b'160805', b'160805 Social Change'),
                            (b'160806', b'160806 Social Theory'),
                            (
                                b'160807',
                                b'160807 Sociological Methodology and Research Methods',
                            ),
                            (
                                b'160808',
                                b'160808 Sociology and Social Studies of Science and Technology',
                            ),
                            (b'160809', b'160809 Sociology of Education'),
                            (
                                b'160810',
                                b'160810 Urban Sociology and Community Studies',
                            ),
                            (
                                b'160899',
                                b'160899 Sociology not elsewhere classified',
                            ),
                            (b'1699', b'1699 OTHER STUDIES IN HUMAN SOCIETY'),
                            (b'169901', b'169901 Gender Specific Studies'),
                            (
                                b'169902',
                                b'169902 Studies of Aboriginal and Torres Strait Islander Society',
                            ),
                            (b'169903', b'169903 Studies of Asian Society'),
                            (b'169904', b'169904 Studies of Maori Society'),
                            (
                                b'169905',
                                b"169905 Studies of Pacific Peoples' Societies",
                            ),
                            (
                                b'169999',
                                b'169999 Studies in Human Society not elsewhere classified',
                            ),
                            (b'17', b'17 PSYCHOLOGY AND COGNITIVE SCIENCES'),
                            (b'1701', b'1701 PSYCHOLOGY'),
                            (
                                b'170101',
                                b'170101 Biological Psychology (Neuropsychology, Psychopharmacology, Physiological Psychology)',
                            ),
                            (
                                b'170102',
                                b'170102 Developmental Psychology and Ageing',
                            ),
                            (b'170103', b'170103 Educational Psychology'),
                            (b'170104', b'170104 Forensic Psychology'),
                            (b'170105', b'170105 Gender Psychology'),
                            (
                                b'170106',
                                b'170106 Health, Clinical and Counselling Psychology',
                            ),
                            (
                                b'170107',
                                b'170107 Industrial and Organisational Psychology',
                            ),
                            (b'170108', b'170108 Kaupapa Maori Psychology'),
                            (
                                b'170109',
                                b'170109 Personality, Abilities and Assessment',
                            ),
                            (
                                b'170110',
                                b'170110 Psychological Methodology, Design and Analysis',
                            ),
                            (b'170111', b'170111 Psychology of Religion'),
                            (
                                b'170112',
                                b'170112 Sensory Processes, Perception and Performance',
                            ),
                            (
                                b'170113',
                                b'170113 Social and Community Psychology',
                            ),
                            (
                                b'170114',
                                b'170114 Sport and Exercise Psychology',
                            ),
                            (
                                b'170199',
                                b'170199 Psychology not elsewhere classified',
                            ),
                            (b'1702', b'1702 COGNITIVE SCIENCES'),
                            (
                                b'170201',
                                b'170201 Computer Perception, Memory and Attention',
                            ),
                            (b'170202', b'170202 Decision Making'),
                            (
                                b'170203',
                                b'170203 Knowledge Representation and Machine Learning',
                            ),
                            (
                                b'170204',
                                b'170204 Linguistic Processes (incl. Speech Production and Comprehension)',
                            ),
                            (
                                b'170205',
                                b'170205 Neurocognitive Patterns and Neural Networks',
                            ),
                            (
                                b'170299',
                                b'170299 Cognitive Sciences not elsewhere classified',
                            ),
                            (
                                b'1799',
                                b'1799 OTHER PSYCHOLOGY AND COGNITIVE SCIENCES',
                            ),
                            (
                                b'179999',
                                b'179999 Psychology and Cognitive Sciences not elsewhere classified',
                            ),
                            (b'18', b'18 LAW AND LEGAL STUDIES'),
                            (b'1801', b'1801 LAW'),
                            (
                                b'180101',
                                b'180101 Aboriginal and Torres Strait Islander Law',
                            ),
                            (b'180102', b'180102 Access to Justice'),
                            (b'180103', b'180103 Administrative Law'),
                            (b'180104', b'180104 Civil Law and Procedure'),
                            (b'180105', b'180105 Commercial and Contract Law'),
                            (b'180106', b'180106 Comparative Law'),
                            (
                                b'180107',
                                b'180107 Conflict of Laws (Private International Law)',
                            ),
                            (b'180108', b'180108 Constitutional Law'),
                            (
                                b'180109',
                                b'180109 Corporations and Associations Law',
                            ),
                            (b'180110', b'180110 Criminal Law and Procedure'),
                            (
                                b'180111',
                                b'180111 Environmental and Natural Resources Law',
                            ),
                            (b'180112', b'180112 Equity and Trusts Law'),
                            (b'180113', b'180113 Family Law'),
                            (b'180114', b'180114 Human Rights Law'),
                            (b'180115', b'180115 Intellectual Property Law'),
                            (
                                b'180116',
                                b'180116 International Law (excl. International Trade Law)',
                            ),
                            (b'180117', b'180117 International Trade Law'),
                            (b'180118', b'180118 Labour Law'),
                            (b'180119', b'180119 Law and Society'),
                            (
                                b'180120',
                                b'180120 Legal Institutions (incl. Courts and Justice Systems)',
                            ),
                            (
                                b'180121',
                                b'180121 Legal Practice, Lawyering and the Legal Profession',
                            ),
                            (
                                b'180122',
                                b'180122 Legal Theory, Jurisprudence and Legal Interpretation',
                            ),
                            (
                                b'180123',
                                b'180123 Litigation, Adjudication and Dispute Resolution',
                            ),
                            (
                                b'180124',
                                b'180124 Property Law (excl. Intellectual Property Law)',
                            ),
                            (b'180125', b'180125 Taxation Law'),
                            (b'180126', b'180126 Tort Law'),
                            (
                                b'180199',
                                b'180199 Law not elsewhere classified',
                            ),
                            (b'1802', b'1802 MAORI LAW'),
                            (
                                b'180201',
                                b'180201 Nga Tikanga Maori (Maori Customary Law)',
                            ),
                            (
                                b'180202',
                                b'180202 Te Maori Whakahaere Rauemi (Maori Resource Law))',
                            ),
                            (
                                b'180203',
                                b'180203 Te Tiriti o Waitangi (The Treaty of Waitangi)',
                            ),
                            (
                                b'180204',
                                b'180204 Te Ture Whenua (Maori Land Law)',
                            ),
                            (
                                b'180299',
                                b'180299 Maori Law not elsewhere classified',
                            ),
                            (b'1899', b'1899 OTHER LAW AND LEGAL STUDIES'),
                            (
                                b'189999',
                                b'189999 Law and Legal Studies not elsewhere classified',
                            ),
                            (
                                b'19',
                                b'19 STUDIES IN CREATIVE ARTS AND WRITING',
                            ),
                            (b'1901', b'1901 ART THEORY AND CRITICISM'),
                            (b'190101', b'190101 Art Criticism'),
                            (b'190102', b'190102 Art History'),
                            (b'190103', b'190103 Art Theory'),
                            (b'190104', b'190104 Visual Cultures'),
                            (
                                b'190199',
                                b'190199 Art Theory and Criticism not elsewhere classified',
                            ),
                            (
                                b'1902',
                                b'1902 FILM, TELEVISION AND DIGITAL MEDIA',
                            ),
                            (b'190201', b'190201 Cinema Studies'),
                            (
                                b'190202',
                                b'190202 Computer Gaming and Animation',
                            ),
                            (b'190203', b'190203 Electronic Media Art'),
                            (b'190204', b'190204 Film and Television'),
                            (b'190205', b'190205 Interactive Media'),
                            (
                                b'190299',
                                b'190299 Film, Television and Digital Media not elsewhere classified',
                            ),
                            (
                                b'1903',
                                b'1903 JOURNALISM AND PROFESSIONAL WRITING',
                            ),
                            (b'190301', b'190301 Journalism Studies'),
                            (b'190302', b'190302 Professional Writing'),
                            (b'190303', b'190303 Technical Writing'),
                            (
                                b'190399',
                                b'190399 Journalism and Professional Writing not elsewhere classified',
                            ),
                            (
                                b'1904',
                                b'1904 PERFORMING ARTS AND CREATIVE WRITING',
                            ),
                            (
                                b'190401',
                                b'190401 Aboriginal and Torres Strait Islander Performing Arts',
                            ),
                            (
                                b'190402',
                                b'190402 Creative Writing (incl. Playwriting)',
                            ),
                            (b'190403', b'190403 Dance'),
                            (
                                b'190404',
                                b'190404 Drama, Theatre and Performance Studies',
                            ),
                            (b'190405', b'190405 Maori Performing Arts'),
                            (b'190406', b'190406 Music Composition'),
                            (b'190407', b'190407 Music Performance'),
                            (b'190408', b'190408 Music Therapy'),
                            (
                                b'190409',
                                b'190409 Musicology and Ethnomusicology',
                            ),
                            (
                                b'190410',
                                b'190410 Pacific Peoples Performing Arts',
                            ),
                            (
                                b'190499',
                                b'190499 Performing Arts and Creative Writing not elsewhere classified',
                            ),
                            (b'1905', b'1905 VISUAL ARTS AND CRAFTS'),
                            (b'190501', b'190501 Crafts'),
                            (
                                b'190502',
                                b'190502 Fine Arts (incl. Sculpture and Painting)',
                            ),
                            (b'190503', b'190503 Lens-based Practice'),
                            (
                                b'190504',
                                b'190504 Performance and Installation Art',
                            ),
                            (
                                b'190599',
                                b'190599 Visual Arts and Crafts not elsewhere classified',
                            ),
                            (
                                b'1999',
                                b'1999 OTHER STUDIES IN CREATIVE ARTS AND WRITING',
                            ),
                            (
                                b'199999',
                                b'199999 Studies in Creative Arts and Writing not elsewhere classified',
                            ),
                            (b'20', b'20 LANGUAGE, COMMUNICATION AND CULTURE'),
                            (b'2001', b'2001 COMMUNICATION AND MEDIA STUDIES'),
                            (b'200101', b'200101 Communication Studies'),
                            (
                                b'200102',
                                b'200102 Communication Technology and Digital Media Studies',
                            ),
                            (
                                b'200103',
                                b'200103 International and Development Communication',
                            ),
                            (b'200104', b'200104 Media Studies'),
                            (
                                b'200105',
                                b'200105 Organisational, Interpersonal and Intercultural Communication',
                            ),
                            (
                                b'200199',
                                b'200199 Communication and Media Studies not elsewhere classified',
                            ),
                            (b'2002', b'2002 CULTURAL STUDIES'),
                            (
                                b'200201',
                                b'200201 Aboriginal and Torres Strait Islander Cultural Studies',
                            ),
                            (b'200202', b'200202 Asian Cultural Studies'),
                            (
                                b'200203',
                                b'200203 Consumption and Everyday Life',
                            ),
                            (b'200204', b'200204 Cultural Theory'),
                            (b'200205', b'200205 Culture, Gender, Sexuality'),
                            (b'200206', b'200206 Globalisation and Culture'),
                            (b'200207', b'200207 Maori Cultural Studies'),
                            (b'200208', b'200208 Migrant Cultural Studies'),
                            (
                                b'200209',
                                b'200209 Multicultural, Intercultural and Cross-cultural Studies',
                            ),
                            (b'200210', b'200210 Pacific Cultural Studies'),
                            (b'200211', b'200211 Postcolonial Studies'),
                            (b'200212', b'200212 Screen and Media Culture'),
                            (
                                b'200299',
                                b'200299 Cultural Studies not elsewhere classified',
                            ),
                            (b'2003', b'2003 LANGUAGE STUDIES'),
                            (b'200301', b'200301 Early English Languages'),
                            (b'200302', b'200302 English Language'),
                            (
                                b'200303',
                                b'200303 English as a Second Language',
                            ),
                            (
                                b'200304',
                                b'200304 Central and Eastern European Languages (incl. Russian)',
                            ),
                            (
                                b'200305',
                                b'200305 Latin and Classical Greek Languages',
                            ),
                            (b'200306', b'200306 French Language'),
                            (b'200307', b'200307 German Language'),
                            (b'200308', b'200308 Iberian Languages'),
                            (b'200309', b'200309 Italian Language'),
                            (b'200310', b'200310 Other European Languages'),
                            (b'200311', b'200311 Chinese Languages'),
                            (b'200312', b'200312 Japanese Language'),
                            (b'200313', b'200313 Indonesian Languages'),
                            (
                                b'200314',
                                b'200314 South-East Asian Languages (excl. Indonesian)',
                            ),
                            (b'200315', b'200315 Indian Languages'),
                            (b'200316', b'200316 Korean Language'),
                            (
                                b'200317',
                                b'200317 Other Asian Languages (excl. South-East Asian)',
                            ),
                            (b'200318', b'200318 Middle Eastern Languages'),
                            (
                                b'200319',
                                b'200319 Aboriginal and Torres Strait Islander Languages',
                            ),
                            (b'200320', b'200320 Pacific Languages'),
                            (
                                b'200321',
                                b'200321 Te Reo Maori (Maori Language)',
                            ),
                            (
                                b'200322',
                                b'200322 Comparative Language Studies',
                            ),
                            (
                                b'200323',
                                b'200323 Translation and Interpretation Studies',
                            ),
                            (
                                b'200399',
                                b'200399 Language Studies not elsewhere classified',
                            ),
                            (b'2004', b'2004 LINGUISTICS'),
                            (
                                b'200401',
                                b'200401 Applied Linguistics and Educational Linguistics',
                            ),
                            (b'200402', b'200402 Computational Linguistics'),
                            (b'200403', b'200403 Discourse and Pragmatics'),
                            (
                                b'200404',
                                b'200404 Laboratory Phonetics and Speech Science',
                            ),
                            (
                                b'200405',
                                b'200405 Language in Culture and Society (Sociolinguistics)',
                            ),
                            (
                                b'200406',
                                b'200406 Language in Time and Space (incl. Historical Linguistics, Dialectology)',
                            ),
                            (b'200407', b'200407 Lexicography'),
                            (
                                b'200408',
                                b'200408 Linguistic Structures (incl. Grammar, Phonology, Lexicon, Semantics)',
                            ),
                            (
                                b'200499',
                                b'200499 Linguistics not elsewhere classified',
                            ),
                            (b'2005', b'2005 LITERARY STUDIES'),
                            (
                                b'200501',
                                b'200501 Aboriginal and Torres Strait Islander Literature',
                            ),
                            (
                                b'200502',
                                b'200502 Australian Literature (excl. Aboriginal and Torres Strait Islander Literature)',
                            ),
                            (
                                b'200503',
                                b'200503 British and Irish Literature',
                            ),
                            (b'200504', b'200504 Maori Literature'),
                            (
                                b'200505',
                                b'200505 New Zealand Literature (excl. Maori Literature)',
                            ),
                            (b'200506', b'200506 North American Literature'),
                            (b'200507', b'200507 Pacific Literature'),
                            (
                                b'200508',
                                b'200508 Other Literatures in English',
                            ),
                            (
                                b'200509',
                                b'200509 Central and Eastern European Literature (incl. Russian)',
                            ),
                            (
                                b'200510',
                                b'200510 Latin and Classical Greek Literature',
                            ),
                            (b'200511', b'200511 Literature in French'),
                            (b'200512', b'200512 Literature in German'),
                            (b'200513', b'200513 Literature in Italian'),
                            (
                                b'200514',
                                b'200514 Literature in Spanish and Portuguese',
                            ),
                            (b'200515', b'200515 Other European Literature'),
                            (b'200516', b'200516 Indonesian Literature'),
                            (b'200517', b'200517 Literature in Chinese'),
                            (b'200518', b'200518 Literature in Japanese'),
                            (
                                b'200519',
                                b'200519 South-East Asian Literature (excl. Indonesian)',
                            ),
                            (b'200520', b'200520 Indian Literature'),
                            (b'200521', b'200521 Korean Literature'),
                            (
                                b'200522',
                                b'200522 Other Asian Literature (excl. South-East Asian)',
                            ),
                            (b'200523', b'200523 Middle Eastern Literature'),
                            (
                                b'200524',
                                b'200524 Comparative Literature Studies',
                            ),
                            (b'200525', b'200525 Literary Theory'),
                            (
                                b'200526',
                                b'200526 Stylistics and Textual Analysis',
                            ),
                            (
                                b'200599',
                                b'200599 Literary Studies not elsewhere classified',
                            ),
                            (
                                b'2099',
                                b'2099 OTHER LANGUAGE, COMMUNICATION AND CULTURE',
                            ),
                            (
                                b'209999',
                                b'209999 Language, Communication and Culture not elsewhere classified',
                            ),
                            (b'21', b'21 HISTORY AND ARCHAEOLOGY'),
                            (b'2101', b'2101 ARCHAEOLOGY'),
                            (
                                b'210101',
                                b'210101 Aboriginal and Torres Strait Islander Archaeology',
                            ),
                            (b'210102', b'210102 Archaeological Science'),
                            (
                                b'210103',
                                b'210103 Archaeology of Asia, Africa and the Americas',
                            ),
                            (
                                b'210104',
                                b'210104 Archaeology of Australia (excl. Aboriginal and Torres Strait Islander)',
                            ),
                            (
                                b'210105',
                                b'210105 Archaeology of Europe, the Mediterranean and the Levant',
                            ),
                            (
                                b'210106',
                                b'210106 Archaeology of New Guinea and Pacific Islands (excl. New Zealand)',
                            ),
                            (
                                b'210107',
                                b'210107 Archaeology of New Zealand (excl. Maori)',
                            ),
                            (
                                b'210108',
                                b'210108 Historical Archaeology (incl. Industrial Archaeology)',
                            ),
                            (b'210109', b'210109 Maori Archaeology'),
                            (b'210110', b'210110 Maritime Archaeology'),
                            (
                                b'210199',
                                b'210199 Archaeology not elsewhere classified',
                            ),
                            (b'2102', b'2102 CURATORIAL AND RELATED STUDIES'),
                            (
                                b'210201',
                                b'210201 Archival, Repository and Related Studies',
                            ),
                            (
                                b'210202',
                                b'210202 Heritage and Cultural Conservation',
                            ),
                            (b'210203', b'210203 Materials Conservation'),
                            (b'210204', b'210204 Museum Studies'),
                            (
                                b'210299',
                                b'210299 Curatorial and Related Studies not elsewhere classified',
                            ),
                            (b'2103', b'2103 HISTORICAL STUDIES'),
                            (
                                b'210301',
                                b'210301 Aboriginal and Torres Strait Islander History',
                            ),
                            (b'210302', b'210302 Asian History'),
                            (
                                b'210303',
                                b'210303 Australian History (excl. Aboriginal and Torres Strait Islander History)',
                            ),
                            (b'210304', b'210304 Biography'),
                            (b'210305', b'210305 British History'),
                            (
                                b'210306',
                                b'210306 Classical Greek and Roman History',
                            ),
                            (
                                b'210307',
                                b'210307 European History (excl. British, Classical Greek and Roman)',
                            ),
                            (b'210308', b'210308 Latin American History'),
                            (b'210309', b'210309 Maori History'),
                            (
                                b'210310',
                                b'210310 Middle Eastern and African History',
                            ),
                            (b'210311', b'210311 New Zealand History'),
                            (b'210312', b'210312 North American History'),
                            (
                                b'210313',
                                b'210313 Pacific History (excl. New Zealand and Maori)',
                            ),
                            (
                                b'210399',
                                b'210399 Historical Studies not elsewhere classified',
                            ),
                            (b'2199', b'2199 OTHER HISTORY AND ARCHAEOLOGY'),
                            (
                                b'219999',
                                b'219999 History and Archaeology not elsewhere classified',
                            ),
                            (b'22', b'22 PHILOSOPHY AND RELIGIOUS STUDIES'),
                            (b'2201', b'2201 APPLIED ETHICS'),
                            (
                                b'220101',
                                b'220101 Bioethics (human and animal)',
                            ),
                            (b'220102', b'220102 Business Ethics'),
                            (
                                b'220103',
                                b'220103 Ethical Use of New Technology (e.g. Nanotechnology, Biotechnology)',
                            ),
                            (
                                b'220104',
                                b'220104 Human Rights and Justice Issues',
                            ),
                            (b'220105', b'220105 Legal Ethics'),
                            (b'220106', b'220106 Medical Ethics'),
                            (
                                b'220107',
                                b'220107 Professional Ethics (incl. police and research ethics)',
                            ),
                            (
                                b'220199',
                                b'220199 Applied Ethics not elsewhere classified',
                            ),
                            (
                                b'2202',
                                b'2202 HISTORY AND PHILOSOPHY OF SPECIFIC FIELDS',
                            ),
                            (b'220201', b'220201 Business and Labour History'),
                            (
                                b'220202',
                                b'220202 History and Philosophy of Education',
                            ),
                            (
                                b'220203',
                                b'220203 History and Philosophy of Engineering and Technology',
                            ),
                            (
                                b'220204',
                                b'220204 History and Philosophy of Law and Justice',
                            ),
                            (
                                b'220205',
                                b'220205 History and Philosophy of Medicine',
                            ),
                            (
                                b'220206',
                                b'220206 History and Philosophy of Science (incl. Non-historical Philosophy of Science)',
                            ),
                            (
                                b'220207',
                                b'220207 History and Philosophy of the Humanities',
                            ),
                        ],
                    ),
                ),
                (
                    'for_percentage_3',
                    models.IntegerField(
                        default=0,
                        choices=[
                            (0, b'0%'),
                            (10, b'10%'),
                            (20, b'20%'),
                            (30, b'30%'),
                            (40, b'40%'),
                            (50, b'50%'),
                            (60, b'60%'),
                            (70, b'70%'),
                            (80, b'80%'),
                            (90, b'90%'),
                            (100, b'100%'),
                        ],
                    ),
                ),
                (
                    'nectar_support',
                    models.CharField(
                        help_text=b'Specify any NeCTAR Virtual Laboratories\n                    supporting this request.',
                        max_length=255,
                        verbose_name=b'List any NeCTAR Virtual Laboratories supporting this request',
                        blank=True,
                    ),
                ),
                (
                    'ncris_support',
                    models.CharField(
                        help_text=b'Specify NCRIS capabilities supporting this request.',
                        max_length=255,
                        verbose_name=b'List NCRIS capabilities supporting this request',
                        blank=True,
                    ),
                ),
                (
                    'funding_national_percent',
                    models.IntegerField(
                        default=b'100',
                        help_text=b'Percentage funded under the National\n                    Allocation Scheme.',
                        error_messages={
                            b'max_value': b'The maximum percent is 100',
                            b'min_value': b'The minimum percent is 0',
                        },
                        verbose_name=b'Nationally Funded Percentage [0..100]',
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                (
                    'funding_node',
                    models.CharField(
                        choices=[
                            (b'nci', b'Australian Capital Territory (NCI)'),
                            (b'intersect', b'New South Wales (Intersect)'),
                            (b'qcif', b'Queensland (QCIF)'),
                            (b'ersa', b'South Australia (eRSA)'),
                            (b'tpac', b'Tasmania (TPAC)'),
                            (b'uom', b'Victoria (Melbourne)'),
                            (b'monash', b'Victoria (Monash)'),
                            (b'pawsey', b'Western Australia (Pawsey)'),
                        ],
                        max_length=128,
                        blank=True,
                        help_text=b'You can choose the node that complements\n                    the National Funding.',
                        null=True,
                        verbose_name=b'Node Funding Remainder (if applicable)',
                    ),
                ),
                (
                    'parent_request',
                    models.ForeignKey(
                        blank=True,
                        to='rcallocation.AllocationRequest',
                        null=True,
                        on_delete=models.SET_NULL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ChiefInvestigator',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'title',
                    models.CharField(
                        help_text=b"The chief investigator's title",
                        max_length=60,
                        verbose_name=b'Title',
                    ),
                ),
                (
                    'given_name',
                    models.CharField(
                        help_text=b"The chief investigator's given name",
                        max_length=200,
                        verbose_name=b'Given name',
                    ),
                ),
                (
                    'surname',
                    models.CharField(
                        help_text=b"The chief investigator's surname",
                        max_length=200,
                        verbose_name=b'Surname',
                    ),
                ),
                (
                    'email',
                    models.EmailField(
                        help_text=b'Email address must belong the university or\n            organisation for accountability.',
                        max_length=254,
                        verbose_name=b'Institutional email address',
                    ),
                ),
                (
                    'institution',
                    models.CharField(
                        help_text=b'The name of the institution or university of\n                    the chief investigator including the schools,\n                    faculty and/or department.',
                        max_length=200,
                        verbose_name=b'Institution',
                    ),
                ),
                (
                    'additional_researchers',
                    models.TextField(
                        default=b'',
                        help_text=b'Please list all other primary investigators, partner\n        investigators and other research collaborators',
                        max_length=1000,
                        verbose_name=b'Please list all other primary investigators, partner investigators and other research collaborators',
                        blank=True,
                    ),
                ),
                (
                    'allocation',
                    models.ForeignKey(
                        related_name='investigators',
                        to='rcallocation.AllocationRequest',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'grant_type',
                    models.CharField(
                        default=b'arc',
                        help_text=b'Choose the grant type from the dropdown options.',
                        max_length=128,
                        verbose_name=b'Type',
                        choices=[
                            (b'arc', b'ARC'),
                            (b'nhmrc', b'NHMRC'),
                            (b'comp', b'Australian competitive grant'),
                            (b'govt', b'Other Australian government grant'),
                            (b'industry', b'Industry funding'),
                            (b'ext', b'Other external funding'),
                            (b'inst', b'Institutional funding'),
                        ],
                    ),
                ),
                (
                    'funding_body_scheme',
                    models.CharField(
                        help_text=b'For example, ARC Discovery Project.',
                        max_length=255,
                        verbose_name=b'Funding body and scheme',
                    ),
                ),
                (
                    'grant_id',
                    models.CharField(
                        help_text=b'Specify the grant id.',
                        max_length=200,
                        verbose_name=b'Grant ID',
                        blank=True,
                    ),
                ),
                (
                    'first_year_funded',
                    models.IntegerField(
                        default=2015,
                        help_text=b'Specify the first year funded',
                        error_messages={
                            b'max_value': b'Please input a year between 1970 ~ 3000',
                            b'min_value': b'Please input a year between 1970 ~ 3000',
                        },
                        verbose_name=b'First year funded',
                        validators=[
                            django.core.validators.MinValueValidator(1970),
                            django.core.validators.MaxValueValidator(3000),
                        ],
                    ),
                ),
                (
                    'total_funding',
                    models.FloatField(
                        help_text=b'Total funding amount in AUD',
                        verbose_name=b'Total funding (AUD)',
                        validators=[
                            django.core.validators.MinValueValidator(1)
                        ],
                    ),
                ),
                (
                    'allocation',
                    models.ForeignKey(
                        related_name='grants',
                        to='rcallocation.AllocationRequest',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'name',
                    models.CharField(
                        help_text=b'List the Australian research institutions and\n                    universities supported by this application. If this\n                    application is just for you, just write the name of\n                    your institution or university. If you are running a\n                    public web service list the Australian research\n                    institutions and universities that\n                    you think will benefit most.',
                        max_length=200,
                        verbose_name=b'Supported institutions',
                    ),
                ),
                (
                    'allocation',
                    models.ForeignKey(
                        related_name='institutions',
                        to='rcallocation.AllocationRequest',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'publication',
                    models.CharField(
                        help_text=b'Please provide any traditional and non-traditional\n                research outputs using a citation style text reference\n                for each. eg. include article/title, journal/outlet, year,\n                DOI/link if available.',
                        max_length=255,
                        verbose_name=b'Publication/Output',
                    ),
                ),
                (
                    'allocation',
                    models.ForeignKey(
                        related_name='publications',
                        to='rcallocation.AllocationRequest',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Quota',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'resource',
                    models.CharField(
                        max_length=64,
                        choices=[
                            (b'volume', b'Volume'),
                            (b'object', b'Object'),
                        ],
                    ),
                ),
                (
                    'zone',
                    models.CharField(
                        help_text=b'The location to of the resource.',
                        max_length=64,
                        verbose_name=b'Availability Zone',
                    ),
                ),
                (
                    'requested_quota',
                    models.IntegerField(
                        default=b'0', verbose_name=b'Requested quota'
                    ),
                ),
                (
                    'quota',
                    models.IntegerField(
                        default=b'0', verbose_name=b'Allocated quota'
                    ),
                ),
                (
                    'units',
                    models.CharField(
                        default=b'GB',
                        max_length=64,
                        verbose_name=b'The units the quota is stored in.',
                    ),
                ),
                (
                    'allocation',
                    models.ForeignKey(
                        related_name='quotas',
                        to='rcallocation.AllocationRequest',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='quota',
            unique_together=set([('allocation', 'resource', 'zone')]),
        ),
        migrations.AlterUniqueTogether(
            name='publication',
            unique_together=set([('allocation', 'publication')]),
        ),
        migrations.AlterUniqueTogether(
            name='institution',
            unique_together=set([('allocation', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='grant',
            unique_together=set(
                [
                    (
                        'allocation',
                        'grant_type',
                        'funding_body_scheme',
                        'grant_id',
                        'first_year_funded',
                        'total_funding',
                    )
                ]
            ),
        ),
    ]
