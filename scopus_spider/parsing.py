""" 
.. module:: parse
    :synopsis: functions for parsing xml 

ARTICLE META DATA TABLE
eid = scopus id
doi = digital online identifier 
prism:aggregationType = journal or whatever
dc:title = title of article
citedby-count = number of forward citations
prism:publicationName
<link href="" rel="self"> = this abstract info
<link href="" rel="cited-by"> = links to outward cites
<abstract, original=""><ce:para> = abstract paragraph (in multiple places)
<source country="" srcid="" type="">
 <sourcetitle> 

MULTI-ID TABLE

<itemid idtype=MULTIPLE!


SUBJECT AREA TABLE?
subject-area, abbrev="*", code=[0-9] = text (MULTIPLE)


AUTHOR TABLE
eid 
author, auid=<>, seq=<> = author id
cd:indexed-name =  
author-url = scopus link to author info


REFERENCES TABLE
under each <referencence>, 
itemid, idtype="SGR" = Scopus EID code
ref-text = text for articles without authors
ref-fulltext = contains authors, title etc.... 
author, seq=[0-9] = author info
- ce:initials
- ce:indexed-name
- ce:surname
ref-sourcetitle = 
ref-publicationyear = 
 


## Edge cases
1- EID 79955512194 Medication Use for trauma systoms and PTSD in pregnant
and breastfeeding women, does not show when searched in scopus. It appears
that it has id, but only because it is a reference. 


"""
from bs4 import BeautifulStoneSoup
import subprocess
import os
import data_tools
import pdb 


class parse_xml:
    """ This is a class of functions that extract text from xml from scopus
    
    
    """
    def __init__(self, xml_text):
        op = open(xml_text,"r").read()
        self.soup = BeautifulStoneSoup(op)

    def xprint(self):
        """ Pretty print xml
        """
        pretty = self.soup.prettify()
        print "test"
        print pretty

    def get_reference(self):
        """ Find all references
        """
        ref = self.soup.find_all('reference')
        print ref[0:2]
        return(ref)
    
    def get_meta(self):
        """ get article meta data 
        """
        # pdb.set_trace()
        core = self.soup.find('coredata')
        eid = core.find('eid').string
        try:
            pubmed_id = core.find('pubmed-id').string
        except:
            pubmed_id = None
        try: 
            doi = core.find('doi').string
        except:
            doi = None
        try:
            pub_name = core.find('publicationName').string.encode('utf-8')
        except:
            pub_name = None
        try:
            issn = core.find('issn').string.encode('utf-8')
        except:
            issn = None 
        title = core.find('title').string.encode('utf-8')
        try:
            abstract = core.find('para').string.encode('utf-8')
        except:
            abstract = None
        source_type = core.find('srctype').string
        try:
            cited_by_url = core.find('link',{"rel":"cited-by"}).get("href")
        except:
            cited_by_url = None
        meta = {"eid":eid, 
                "pubmed-id":pubmed_id, "doi":doi,
                "pub_name":pub_name,
                "issn":issn,
                "title":title,"abstract":abstract, 
                "source_type":source_type,"cited_by_url":cited_by_url}
        return([meta])
    
    def get_authors(self):
        """ get article meta data 
        """
        core = self.soup.find('coredata')
        eid = core.find('eid').string
        try:
            pubmed_id = core.find('pubmed-id').string
        except: 
            pubmed_id = None
        auths = self.soup.find('authors')
        print(eid)
        d_auth = {}
        for auth in auths.contents:
            author_id = auth.get('auid')
            author_seq = auth.get("seq")
            author_name = auth.find('indexed-name').contents[0].encode('utf-8')
            author_surname = auth.find('surname').contents[0].encode('utf-8')
            try:
                author_given = auth.find('given-name').contents[0].encode('utf-8')
            except:
                author_given = None
            try:
                author_aff_id = auth.find('affiliation').get('id')
            except:
                author_aff_id = None
            da = {"eid":eid,
                  "pubmed_id":pubmed_id,
                  "author_id":author_id,
                  "author_seq":author_seq,
                  "author_name":author_name,
                  "author_surname":author_surname,
                  "author_given":author_given,
                  "author_aff_id":author_aff_id
                  }
            if len(d_auth) == 0:
                d_auth = [da]  
            else:
                d_auth.append(da)
        #pdb.set_trace()
        
        return(d_auth)
    
    def get_references(self):
        """ get references data 
        """
        core = self.soup.find('coredata')
        eid = core.find('eid').string
        try:
            pubmed_id = core.find('pubmed-id').string
        except: 
            pubmed_id = None
        try: 
            bib = self.soup.find_all('reference')
        except:
            d_refs = None
        print(eid)
        d_refs = {}
        for ref in bib:
            ref_id = "2-s2.0-" + ref.find('itemid').contents[0]
            try:
                ref_title = ref.find('ref-titletext').contents[0].encode('utf-8')
            except:
                ref_title = None
            ref_authors_cnt = len(ref.find_all('author'))
            da = {"eid":eid,
                  "pubmed_id":pubmed_id,
                  "ref_id":ref_id,
                  "ref_title":ref_title,
                  "ref_authors_cnt":ref_authors_cnt
                  }
            if len(d_refs) == 0:
                d_refs = [da]  
            else:
                d_refs.append(da)
        #pdb.set_trace()
        return(d_refs)

    def get_coauthors(self, primary_authid):
        """ get references data 
        """
        try: 
            entries = self.soup.find_all('entry')
        except:
            entries = None
        ls_auths = list()
        for entry in entries:
            try:
                eid = entry.find('eid').string
            except:
                eid = None
            try:
                pubmed_id = entry.find('pubmed-id').contents[0].encode('utf-8')
            except:
                pubmed_id = None
            auths = entry.find_all('author')
            for auth in auths:
                d_auth = {}
                d_auth['primary_authid'] = primary_authid
                # d_auth['secondary_authid'] = secondary_authid
                d_auth['eid'] = eid
                d_auth['pubmed_id'] = pubmed_id
                try:
                    d_auth['author_id'] = auth.find('authid').string
                except:
                    d_auth['author_id'] = None
                try:
                    d_auth['author_name'] = auth.find('authname').string.encode('utf-8')
                except:
                    d_auth['author_name'] = None
                try:
                    d_auth['author_surname'] = auth.find('surname').string.encode('utf-8')
                except:
                    d_auth['author_surname'] = None
                try:
                    d_auth['author_given'] = auth.find('given-name').string.encode('utf-8')
                except:
                    d_auth['author_given'] = None
                try:
                    d_auth['author_aff_id'] = auth.find('afid').string
                except:
                    d_auth['author_aff_id'] = None
                ls_auths.append(d_auth)
                
        return(ls_auths)

    
    def get_authors2(self, primary_authid, secondary_authid):
        """ get references data 
        """
        try: 
            entries = self.soup.find_all('entry')
        except:
            entries = None
        ls_auths = list()
        for entry in entries:
            try:
                eid = entry.find('eid').string
            except:
                eid = None
            try:
                pubmed_id = entry.find('pubmed-id').contents[0].encode('utf-8')
            except:
                pubmed_id = None
            auths = entry.find_all('author')
            for auth in auths:
                d_auth = {}
                d_auth['primary_authid'] = primary_authid
                d_auth['secondary_authid'] = secondary_authid
                d_auth['eid'] = eid
                d_auth['pubmed_id'] = pubmed_id
                try:
                    d_auth['author_id'] = auth.find('authid').string
                except:
                    d_auth['author_id'] = None
                try:
                    d_auth['author_name'] = auth.find('authname').string.encode('utf-8')
                except:
                    d_auth['author_name'] = None
                try:
                    d_auth['author_surname'] = auth.find('surname').string.encode('utf-8')
                except:
                    d_auth['author_surname'] = None
                try:
                    d_auth['author_given'] = auth.find('given-name').string.encode('utf-8')
                except:
                    d_auth['author_given'] = None
                try:
                    d_auth['author_aff_id'] = auth.find('afid').string
                except:
                    d_auth['author_aff_id'] = None
                ls_auths.append(d_auth)
                
        return(ls_auths)

    def get_cited_by(self, eid):
            """ get references data 
            """
            eid = eid[:-4]
            try: 
                error = self.soup.find('error')
                print error
            except:
                error = None
            if error is None:
                try: 
                    entries = self.soup.find_all('entry')
                except:
                    d_entries = None
                print(eid)
                d_entries = {}
                for entry in entries:
                    try:
                        citedby_eid = entry.find('eid').contents[0]
                    except:
                        citedby_eid = None
                    try:
                        pubmed_id = entry.find('pubmed-id').contents[0].encode('utf-8')
                    except:
                        pubmed_id = None
                    try:
                        entry_title = entry.find('title').contents[0].encode('utf-8')
                    except:
                        entry_title = None
                    try:
                        entry_journal = entry.find('publicationName').contents[0].encode('utf-8')
                    except:
                        entry_journal = None
                    try:
                        entry_lead_author = entry.find('creator').contents[0].encode('utf-8')
                    except:
                        entry_lead_author = None
                    try:
                        entry_affiliation = entry.find('affilname').contents[0].encode('utf-8')
                    except:
                        entry_affiliation = None
                    try:
                        entry_doi = entry.find('doi').contents[0]
                    except:
                        entry_doi = None
                    try:
                        entry_cited_by_cnt = entry.find('citedby-count').contents[0]
                    except:
                        entry_cited_by_cnt = None
                    da = {"eid":eid, "citedby_eid":citedby_eid, "pubmed_id":pubmed_id,
                          "entry_title":entry_title,
                          "entry_journal":entry_journal,
                          "entry_lead_author":entry_lead_author,
                          "entry_affiliation":entry_affiliation,
                          "entry_doi":entry_doi,
                          "entry_cited_by_cnt":entry_cited_by_cnt
                          }
                    if len(d_entries) == 0:
                        d_entries = [da]  
                    else:
                        d_entries.append(da)
            else:
                d_entries = [{"eid":eid, "citedby_eid":None, "pubmed_id":None,
                          "entry_title":None,
                          "entry_journal":None,
                          "entry_lead_author":None,
                            "entry_affiliation":None,
                          "entry_doi":None,
                          "entry_cited_by_cnt":None
                          }]
            return(d_entries)
    
    def get_soup(self):
        """ return the soup object so that I can do interactive work
        """

        return(self.soup)

# f = open("xml_pretty.xml","w")
# f.write(pretty.encode('utf-8'))
# tag = soup.author
# tag = soup.find_all('dc:creator')
# print tag
## for webscraping
## http://selenium-python.readthedocs.org/

