-- delete linked entries of metadatablock
DELETE FROM public.datasetfieldtype WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'optical_measurements');

-- delete metadatablock
DELETE FROM public.dataverse_metadatablock WHERE metadatablocks_id = (SELECT id FROM public.metadatablock WHERE name = 'optical_measurements');
DELETE FROM public.metadatablock WHERE name = 'optical_measurements';



-- delete linked entries of metadatablock
DELETE FROM public.datasetfieldtype WHERE metadatablock_id = (SELECT id FROM public.metadatablock WHERE name = 'addition_citation');

-- delete metadatablock
DELETE FROM public.dataverse_metadatablock WHERE metadatablocks_id = (SELECT id FROM public.metadatablock WHERE name = 'addition_citation');
DELETE FROM public.metadatablock WHERE name = 'addition_citation';