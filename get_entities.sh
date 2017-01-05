#!/bin/bash

# set -x #debug

declare document_id=$1

declare original_text=$2

declare text=${2,,} # ,, mean lowercase
text=$(sed "s/[^[:alpha:][:digit:][:space:]]/./g" <<< $text) # replace special characters
#text=$(tr '[[:space:]]' ' ' <<< $text) # standard space
text=$(sed -e 's/^ *//' -e 's/ *$//' <<< $text) # remove leading and trailing whitespace
text=$(sed -e 's/[[:space:]]\+/ /' <<< $text) # remove multiple whitespace
text=$(tr ' ' '\n' <<< $text | grep -v -w -f stopwords.txt | egrep '[[:alpha:]]{3,}' | tr '\n' ' ') # only words with 3 chars and remove stopwords 


declare piped_text=$(sed -e 's/ \+/|/g' <<< $text) 
declare piped_pair_text1=$(sed -e 's/\([^ ]\+ \+[^ ]\+\) /\1|/g' <<< $text" XXX" | sed 's/|[^|]*$//') 
declare piped_pair_text2=$(sed -e 's/\([^ ]\+ \+[^ ]\+\) /\1|/g' <<< "XXX "$text | sed 's/^[^|]*|//')
declare piped_pair_text=$piped_pair_text1'|'$piped_pair_text2


declare get_entities_source_word1_result=''
get_entities_source_word1 () {
	local labels=$1
	if [ ${#piped_text} -ge 2 ]; then
		local matches=$(egrep '^('$piped_text')$' $labels | tr '\n' '|')
		if [ ${#matches} -ge 2 ]; then
		    get_entities_source_word1_result=$(egrep -iaob $matches <<< "$original_text")
		fi
	fi
}

declare get_entities_source_word2_result=''
get_entities_source_word2 () {
	local labels=$1
	if [ ${#piped_pair_text} -ge 2 ]; then
		local matches=$(egrep '^('$piped_pair_text')$' $labels | tr '\n' '|')
		if [ ${#matches} -ge 2 ]; then
		    get_entities_source_word2_result=$(egrep -iaob "$matches" <<< "$original_text")
		fi
	fi
}

declare get_entities_source_words_result=''
get_entities_source_words () {
	local labels2=$1
	local labels=$2
	if [ ${#piped_pair_text} -ge 2 ]; then
		local matches=$(egrep '^('$piped_pair_text')$' $labels2 | grep '[[:alpha:]]{5,}' | tr '\n' '|')	
		if [ ${#matches} -ge 2 ]; then
		    local fullmatches=$(egrep '^('$matches')' $labels | tr '\n' '|')
		fi
		if [ ${#fullmatches} -ge 2 ]; then
			get_entities_source_words_result=$(egrep -iaob "$fullmatches" <<< "$original_text")
		fi
	fi
}

declare get_entities_source_words_result=''
get_entities_source () {
	local source=$1
	echo "== BEGIN SOURCE == $source =="	
	cd data/

	SAVEIFS=$IFS; IFS=$(echo -en "");

 	local result1=$(get_entities_source_word1 $source\_word1.txt && echo $get_entities_source_word1_result &)
		
	local result2=$(get_entities_source_word2 $source\_word2.txt && echo $get_entities_source_word2_result &)
	
	local result3=$(get_entities_source_words $source\_words2.txt $source\_words.txt && echo $get_entities_source_words_result &)
		
	wait 
	cd ..

	local result=$result1$'\n'$result2$'\n'$result3
	result=$(sed '{/^$/d}' <<< $result) # remove empty lines
	result=$(awk -F: '{ print '"$document_id"',"\t",$1,"\t",length($2),"\t",$2,"\t",1-1/log(length($2)) }' <<< $result) # convert to the output format 
	echo $result
	echo "== END SOURCE =="
	}

for i in $(ls data/*words.txt | xargs -i basename {} _words.txt); do 
    get_entities_source $i
done