rule XYLENT_TEST_PDF {
	meta:
		description = "Detection of word file designed as a harmless test sample for Xylent Antivirus"
      	author = "Rutuj Runwal"
      	reference = "ADD_GITHUB_REFERENCE"
        score = 90	

	strings:
        $magic = { 25 50 44 46 }
		$s1 = "Rutuj"
		$s2 = "Runwal"
		$s3 = "Xylent"

	condition:
		$magic at 0 and all of ($s*)
}