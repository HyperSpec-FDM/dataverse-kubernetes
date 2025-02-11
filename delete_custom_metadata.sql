-- delete linked entries in datasetfield_controlledvocabularyvalue
DELETE FROM datasetfield_controlledvocabularyvalue
WHERE controlledvocabularyvalues_id IN (
    SELECT id FROM controlledvocabularyvalue
    WHERE datasetfieldtype_id IN (
        SELECT id FROM public.datasetfieldtype
        WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'addition_citation')
    )
);

-- delete linked entries in controlledvocabularyvalue
DELETE FROM controlledvocabularyvalue
WHERE datasetfieldtype_id IN (
    SELECT id FROM public.datasetfieldtype
    WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'addition_citation')
);

-- delete linked entries of datasetfield
DELETE FROM datasetfield
WHERE datasetfieldtype_id IN (
    SELECT id FROM datasetfieldtype
    WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'addition_citation')
);

-- delete linked entries of datasetfieldtype
DELETE FROM public.datasetfieldtype WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'addition_citation');

-- delete metadatablock
DELETE FROM public.dataverse_metadatablock WHERE metadatablocks_id = (SELECT id FROM public.metadatablock WHERE name = 'addition_citation');
DELETE FROM public.metadatablock WHERE name = 'addition_citation';


-- delete linked entries in datasetfield_controlledvocabularyvalue
DELETE FROM datasetfield_controlledvocabularyvalue
WHERE controlledvocabularyvalues_id IN (
    SELECT id FROM controlledvocabularyvalue
    WHERE datasetfieldtype_id IN (
        SELECT id FROM public.datasetfieldtype
        WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'sample_information')
    )
);

-- delete linked entries in controlledvocabularyvalue
DELETE FROM controlledvocabularyvalue
WHERE datasetfieldtype_id IN (
    SELECT id FROM public.datasetfieldtype
    WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'sample_information')
);

-- delete linked entries of datasetfield
DELETE FROM datasetfield
WHERE datasetfieldtype_id IN (
    SELECT id FROM datasetfieldtype
    WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'sample_information')
);

-- delete linked entries of datasetfieldtype
DELETE FROM public.datasetfieldtype WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'sample_information');

-- delete metadatablock
DELETE FROM public.dataverse_metadatablock WHERE metadatablocks_id = (SELECT id FROM public.metadatablock WHERE name = 'sample_information');
DELETE FROM public.metadatablock WHERE name = 'sample_information';


-- delete linked entries in datasetfield_controlledvocabularyvalue
DELETE FROM datasetfield_controlledvocabularyvalue
WHERE controlledvocabularyvalues_id IN (
    SELECT id FROM controlledvocabularyvalue
    WHERE datasetfieldtype_id IN (
        SELECT id FROM public.datasetfieldtype
        WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'mass_spectrometry_imaging')
    )
);

-- delete linked entries in controlledvocabularyvalue
DELETE FROM controlledvocabularyvalue
WHERE datasetfieldtype_id IN (
    SELECT id FROM public.datasetfieldtype
    WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'mass_spectrometry_imaging')
);

-- delete linked entries of datasetfield
DELETE FROM datasetfield
WHERE datasetfieldtype_id IN (
    SELECT id FROM datasetfieldtype
    WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'mass_spectrometry_imaging')
);

-- delete linked entries of datasetfieldtype
DELETE FROM public.datasetfieldtype WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'mass_spectrometry_imaging');

-- delete metadatablock
DELETE FROM public.dataverse_metadatablock WHERE metadatablocks_id = (SELECT id FROM public.metadatablock WHERE name = 'mass_spectrometry_imaging');
DELETE FROM public.metadatablock WHERE name = 'mass_spectrometry_imaging';


-- delete linked entries in datasetfield_controlledvocabularyvalue
DELETE FROM datasetfield_controlledvocabularyvalue
WHERE controlledvocabularyvalues_id IN (
    SELECT id FROM controlledvocabularyvalue
    WHERE datasetfieldtype_id IN (
        SELECT id FROM public.datasetfieldtype
        WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'optical_spectroscopy_imaging')
    )
);

-- delete linked entries in controlledvocabularyvalue
DELETE FROM controlledvocabularyvalue
WHERE datasetfieldtype_id IN (
    SELECT id FROM public.datasetfieldtype
    WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'optical_spectroscopy_imaging')
);

-- delete linked entries of datasetfield
DELETE FROM datasetfield
WHERE datasetfieldtype_id IN (
    SELECT id FROM datasetfieldtype
    WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'optical_spectroscopy_imaging')
);

-- delete linked entries of datasetfieldtype
DELETE FROM public.datasetfieldtype WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'optical_spectroscopy_imaging');

-- delete metadatablock
DELETE FROM public.dataverse_metadatablock WHERE metadatablocks_id = (SELECT id FROM public.metadatablock WHERE name = 'optical_spectroscopy_imaging');
DELETE FROM public.metadatablock WHERE name = 'optical_spectroscopy_imaging';