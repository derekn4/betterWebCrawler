import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urljoin

'''
Derek Nguyen - 44096504
Alex Meng - 12907102
'''


stop_words = ['about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren",
              'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
              "can", 'cannot', 'could', "couldn", 'did', "didn", 'do', 'does', "doesn", 'doing', "don",
              'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn", 'has', "hasn", 'have',
              "haven't", 'having', 'he', 'her', 'here', 'hers', 'herself', 'him',
              'himself', 'his', 'how', "how's", 'if', 'in', 'into', 'is',
              "isn", 'it', 'its', 'itself', 'me', 'more', 'most', "mustn", 'my', 'myself',
              'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our',
              'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she',
              'should', "shouldn", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs',
              'them', 'themselves', 'then', 'there', 'these', 'they',
              'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn",
              'we', 'were', "weren", 'what', 'when',
              'where', 'which', 'while', 'who', 'whom', 'why', 'with', "won",
              'would', "wouldn", 'you', "ll", "re", "ve", 'your', 'yours', 'yourself',
              'yourselves']

crawled_dict = dict()
word_dict = dict()
defrag_dict = dict()

max_pg_len = 0
max_url = ""
subdomains = dict()
subdom_list = []
subdomain_list = []


# 1. Count how many unique pages (unique url dict)
# 2. Longest page in terms of number of words
# using dictionary

# 3. 50 most common words in entire search (ignore stop_words)
#       list of common words, ordered by frequency
#       take dictionary of words and append to list ordered by frequency

# 4. Count subdomains, submit list of subdomains (ordered alphabetically)
#       number of unique pages per subdomain
#       list?


# Text files: unique URLS, length of URLS, subdomains


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation requred

    # open file to track unique pages
    # open file to track longest pages
    # open file to track word counts
    url_file = open("unique_urls.txt", "a+", encoding="utf-8")  # file to read the unique urls
    longest = open("longest_url.txt", 'a+', encoding="utf-8")  # file to save the url having the longest length.
    sub_list = open("subdomains.txt", 'a+', encoding="utf-8") #file to save ics.uci.edu subdomains

    output = []  # list of links in url page
    words = []  # list of words/tokens on url page

    parsed = urlparse(url)

    domain = 'https://' + parsed.netloc

    if resp.status >= 200 and resp.status <= 299:
        if is_valid(url) and check_dup(url):
            html_text = resp.raw_response.content
            content = BeautifulSoup(html_text, "html.parser")

            token_list = get_tokens(content, words)

            # write to url file that tracks unique pages (aka store Document)
            if len(token_list) >= 200:
                defrag = urllib.parse.urldefrag(url)[0]
                if check_dup_defrag(defrag):
                    url_file.write(defrag + '\n')

                global max_pg_len

                #Store longest Page URL
                if (len(token_list) > max_pg_len):
                    max_pg_len = len(token_list)
                    longest.truncate(0)
                    longest.write(url + ' ' + str(max_pg_len) + '\n')

                # Calculating word frequencies (EXCLUDING STOP WORDS)
                for word in token_list:
                    if word not in stop_words:
                        if word not in word_dict.keys():
                            word_dict[word] = 1
                        else:
                            word_dict[word] += 1

                check_freq(word_dict)

            for url in content.find_all('a'):
                # url stuff + append to output links list
                relative = url.get('href')

                if relative is not None:
                    if relative.startswith('/', 0, 1):
                        relative = urljoin(domain, relative)
                    if (not relative.startswith('http', 0, 4)):
                        relative = 'https://' + relative

                defrag_url = urllib.parse.urldefrag(relative)[0]
                if (is_valid(defrag_url)):
                    output.append(defrag_url)

            #count subdomains
            if "ics.uci.edu" in parsed.netloc:
                netlist = parsed.netloc.split(".")
                if netlist[0]!="ics" and parsed.netloc not in subdomains.keys():
                    subdomains[parsed.netloc] = len(output)
                    add_sub = parsed.netloc + ", " + str(len(output))
                    if parsed.netloc not in subdomain_list:
                        subdomain_list.append(parsed.netloc)
                        add_sub = add_sub.lower()
                        subdom_list.append(add_sub)
                        final = sorted(subdom_list)
                        sub_list.truncate(0)
                        sub_list.write(str(final))
    return output

def get_tokens(content, words):
    tokens = []
    for t in content.text.split():
        tokens = re.split(r'[^a-z0-9]+', t.lower())
        words.extend(tokens)

    for word in words:
        if len(word) >= 2 and not word.isdigit():
            tokens += [word]

    return tokens


def check_dup(url):
    if url not in crawled_dict.keys():
        crawled_dict[url] = 1
        return True
    else:
        crawled_dict[url] += 1
        return False

def check_dup_defrag(url):
    if url not in defrag_dict.keys():
        defrag_dict[url] = 1
        return True
    else:
        defrag_dict[url] += 1
        return False

def check_freq(word_dict):
    common_words = open("common_words.txt", 'a+', encoding="utf-8")
    most_common = open("Top_50.txt",  'a+', encoding="utf-8")
    sort_dict = {k: v for k,v in sorted(word_dict.items(), key=lambda item: item[1], reverse=True)}

    # file to store all common words
    common_words.truncate(0)
    common_words.write(str(sort_dict))
    common_words.write('\n')

    #Gets 50 most common words and inputs into a list
    #write list into text file
    most_list=[]
    count = 0
    for i in sort_dict.keys():
        if count == 50:
            break
        else:
            most_list.append(i)
            count += 1

    most_common.truncate(0)
    most_common.write(str(most_list))
    most_common.write('\n')


def is_valid(url):
    try:
        validDoms = ['ics.uci.edu', 'cs.uci.edu', 'informatics.uci.edu', 'stat.uci.edu', 'today.uci.edu']

        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False

        netloc = parsed.netloc
        url_path = parsed.path

        if netloc.startswith("www."):
            netloc = netloc.strip("www.")

        netlist = netloc.split(".")
        sub = ".".join(netlist)

        if len(netlist) >= 4:
            sub = ".".join(netlist[1:])

        if url == "https://ngs.ics.uci.edu/bangalore-and-hyderabad":
            return False

        if url == 'http://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018':
            return False

        if netloc == "today.uci.edu":
            if "/department/information_computer_sciences" not in url_path or "calendar" in url_path:
                return False

        if netloc == "wics.ics.uci.edu":
            if "events" in url_path or "event" in url_path:
                return False
            for param in ["img_", "afg", 'share=']:
                if param in parsed.query:
                    return False

        if netloc == "archive.ics.uci.edu":
            return False

        if netloc == "hack.ics.uci.edu" and "gallery" in url_path:
            return False

        if netloc == "hack.ics.uci.edu" and "img" in url_path:
            return False

        if netloc == "grape.ics.uci.edu":
            return False

        if netloc == "intranet.ics.uci.edu":
            return False

        if netloc == "swiki.ics.uci.edu":
            return False

        if netloc == "cbcl.ics.uci.edu":
            return False

        for netloc in validDoms:
            if sub == netloc:
                return True
            else:
                return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise
