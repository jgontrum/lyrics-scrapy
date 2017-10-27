# Lyrics Scrapy

Scrapy based web crawler for song lyrics.

Crawls all song pages on MetroLyrics.com and indexes them into elasticsearch. Please remember copyright of lyrics and stuff, the usage of the data is only intended for personal use.

## Build
Run `make` and make (haha) sure that you have Python 3.6 installed.

## Data
```json
{
  "artist": "<ARTIST>",
  "artist_id": "artist",
  "artist_popularity": 17.84,
  "album": "<ALBUMNAME>",
  "year": 2005,
  "title": "<SONG TITLE>",
  "song_id": "song-title-artist",
  "lyrics": "This song is dope af.",
  "language": "en"
}
```

## Elasticsearch

Suggested mappings and settings for the elasticsearch index:

```json
{
	"settings": {
		"index": {
			"number_of_shards": 1,
			"number_of_replicas": 0
		},
		"analysis": {
			"filter": {
				"english_stop": {
					"type": "stop",
					"stopwords": "_english_"
				},
				"english_stemmer": {
					"type": "stemmer",
					"language": "english"
				},
				"english_possessive_stemmer": {
					"type": "stemmer",
					"language": "possessive_english"
				}
			},
			"analyzer": {
				"english_case_sensitive": {
					"tokenizer": "standard",
					"filter": [
						"english_possessive_stemmer",
						"english_stop",
						"english_stemmer"
					]
				}
			}
		}
	},
	"mappings": {
		"song": {
			"properties": {
				"artist": {
					"type": "keyword"
				},
				"artist_id": {
					"type": "keyword"
				},
				"album": {
					"type": "keyword"
				},
				"title": {
					"type": "keyword"
				},
				"song_id": {
					"type": "keyword"
				},
				"language": {
					"type": "keyword"
				},
				"genre": {
					"type": "keyword"
				},
				"year": {
					"type": "integer"
				},
				"artist_popularity": {
					"type": "float"
				},
				"song_popularity": {
					"type": "float"
				},
				"lyrics": {
					"type": "text",
					"fields": {
						"analyzed": {
							"type": "text",
							"analyzer": "english"
						},
						"analyzed_case": {
							"type": "text",
							"analyzer": "english_case_sensitive"
						},
						"raw": {
							"type": "text",
							"analyzer": "keyword"
						}
					}
				}
			}
		}
	}
}
```
