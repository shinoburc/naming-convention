#!/usr/bin/perl

use CGI;
use Text::MeCab;
use DBI;
use HTML::Entities;

my $cgi = new CGI;
print $cgi->header(-charset=>"utf-8");

my $title = "Naming";

#print &genEnglish();
#exit;
#&naming(('q', '社会福祉'));
#&naming($cgi);
#exit;

if(defined $cgi->param('action')){
  &naming($cgi);
} else {
  &print_index;
}


sub naming($){
  my $cgi = shift;

  foreach my $query (split /\n/, $cgi->param('q')){
    print &doNaming($query, $cgi);
    print "<br />";
  }
}

sub doNaming($$){
  my $query = shift;
  my $cgi = shift;
  my $m = Text::MeCab->new();

  $query = &dictionary($query, $cgi);
  my $n = $m->parse($query);

  my @result;
  if($cgi->param('naming_style') eq 'hepburn'){
    @result = &genHepburn($n, $cgi);
  } else {
    @result = &genEnglish($n, $cgi);
  }

  my $result = join($cgi->param('separate'), @result);
  if($cgi->param('first_letter_always_lowercase') eq 'true'){
    $result = lcfirst($result);
  }
  $result = $cgi->param('prefix') . $result . &suffix($cgi->param('suffix'), $result);
  return $result;
}

sub genHepburn($$){
  my $n = shift;
  my $cgi = shift;

  my @result;
  while ($n) {
    my $letter;
    my @features = split(/,/, $n->feature);
    if($features[0] ne "BOS/EOS"){
      if($features[5] eq "*"){
        $letter = $n->surface;
        $letter =~ tr/ァ-ン/ぁ-ん/;
      } else {
        $letter = $features[5];
      }
      $letter = &kana2hepburn($letter, $cgi);
      $letter = &case_sensitivity($letter, $cgi);
      push(@result, $letter);
    }
    $n = $n->next;
  }
  return @result;
}

sub genEnglish($$){
  my $n = shift;
  my $cgi = shift;

  my $dbh = DBI->connect("dbi:Pg:dbname=vocation_production", "vocation", "");

  my @letters;
  my @conditions;
  while ($n) {
    my $letter;
    my @features = split(/,/, $n->feature);
    if($features[0] ne "BOS/EOS"){
      push(@letters, $n->surface);
      push(@conditions, "j = " . $dbh->quote($n->surface));
    }
    $n = $n->next;
  }

  my $stmt = $dbh->prepare("select j, e from jtoe where " . join(' or ', @conditions) . " order by length(j) desc");
  $stmt->execute();

  while(my @sql_result =$stmt->fetchrow()){
    for(my $i = 0; $i < @letters; $i++){
      my $letter = $letters[$i];
      $letter =~ s/$sql_result[0]/$sql_result[1]/g;
      $letters[$i] = $letter;
    }
  }

  my @result;
  foreach my $letter(@letters){
    foreach my $word (split / /,$letter){
      $word = &case_sensitivity($word, $cgi);
      push(@result, $word);
    }
  }

  $stmt->finish();
  $dbh->disconnect();

  return @result;
}

sub suffix($$){
  my $suffix = shift;
  my $result = shift;

  $result = lcfirst($result);
  $suffix =~ s/\\1/$result/g;
  $suffix =~ s/\\n/<br\/>/g;
  return $suffix;
}

sub dictionary($$){
  my $query = shift;
  my $cgi = shift;
  my %dictionary = ();
  foreach my $dictionary_line (split /\n/, $cgi->param('dictionary')){
    my($from,$to) = split /=/, $dictionary_line;
    $dictionary{$dictionary_line} = length($from);
  }
  foreach(sort {$dictionary{$b} <=> $dictionary{$a}} keys %dictionary){
    my($from,$to) = split /=/, $_;
    $query =~ s/$from/$to/g;
  }

  return $query;
}

sub case_sensitivity($$){
  my $query = shift;
  my $cgi = shift;
  my $case = $cgi->param('case_ensitivity');

  if($case eq 'upper case'){
    $query = uc($query);
  } elsif($case eq 'lower case'){
    $query = lc($query);
  } elsif($case eq 'upper case first'){
    $query = ucfirst(lc($query));
  } elsif($case eq 'lower case first'){
    $query = lcfirst(uc($query));
  } else {
  }
  return $query;
}

sub escape($){
  my $str = shift;
  return encode_entities($str, q{&<>"'});
  #return encode_entities($str, "<>&");
}

sub kana2hepburn($)
{
    my $kana = shift;
    $_ = $kana;

# 促音は 'ち', 'ちゃ', 'ちゅ', 'ちょ' 音に限りその前にTを加える

    s/っち(?!ゃ|ゅ|ょ)/TCHI/g;
    s/っちゃ/TCHA/g;
    s/っちゅ/TCHU/g;
    s/っちょ/TCHO/g;

# ヘボン式ローマ字つづり一覧表

    s/あ/A/g;
    s/い/I/g;
    s/う/U/g;
    s/え/E/g;
    s/お/O/g;
    s/か/KA/g;
    s/き(?!ゃ|ゅ|ょ)/KI/g;
    s/く/KU/g;
    s/け/KE/g;
    s/こ/KO/g;
    s/さ/SA/g;
    s/し(?!ゃ|ゅ|ょ)/SHI/g;
    s/す/SU/g;
    s/せ/SE/g;
    s/そ/SO/g;
    s/た/TA/g;
    s/ち(?!ゃ|ゅ|ょ)/CHI/g;
    s/つ/TSU/g;
    s/て/TE/g;
    s/と/TO/g;
    s/な/NA/g;
    s/に(?!ゃ|ゅ|ょ)/NI/g;
    s/ぬ/NU/g;
    s/ね/NE/g;
    s/の/NO/g;
    s/は/HA/g;
    s/ひ(?!ゃ|ゅ|ょ)/HI/g;
    s/ふ/FU/g;
    s/へ/HE/g;
    s/ほ/HO/g;
    s/ま/MA/g;
    s/み(?!ゃ|ゅ|ょ)/MI/g;
    s/む/MU/g;
    s/め/ME/g;
    s/も/MO/g;
    s/や/YA/g;
    s/ゆ/YU/g;
    s/よ/YO/g;
    s/ら/RA/g;
    s/り(?!ゃ|ゅ|ょ)/RI/g;
    s/る/RU/g;
    s/れ/RE/g;
    s/ろ/RO/g;
    s/わ/WA/g;
    s/ん/N/g;
    s/が/GA/g;
    s/ぎ(?!ゃ|ゅ|ょ)/GI/g;
    s/ぐ/GU/g;
    s/げ/GE/g;
    s/ご/GO/g;
    s/ざ/ZA/g;
    s/じ(?!ゃ|ゅ|ょ)/JI/g;
    s/ず/ZU/g;
    s/ぜ/ZE/g;
    s/ぞ/ZO/g;
    s/だ/DA/g;
    s/ぢ/JI/g;
    s/づ/ZU/g;
    s/で/DE/g;
    s/ど/DO/g;
    s/ば/BA/g;
    s/び(?!ゃ|ゅ|ょ)/BI/g;
    s/ぶ/BU/g;
    s/べ/BE/g;
    s/ぼ/BO/g;
    s/ぱ/PA/g;
    s/ぴ(?!ゃ|ゅ|ょ)/PI/g;
    s/ぷ/PU/g;
    s/ぺ/PE/g;
    s/ぽ/PO/g;
    s/きゃ/KYA/g;
    s/きゅ/KYU/g;
    s/きょ/KYO/g;
    s/しゃ/SHA/g;
    s/しゅ/SHU/g;
    s/しょ/SHO/g;
    s/ちゃ/CHA/g;
    s/ちゅ/CHU/g;
    s/ちょ/CHO/g;
    s/にゃ/NYA/g;
    s/にゅ/NYU/g;
    s/にょ/NYO/g;
    s/ひゃ/HYA/g;
    s/ひゅ/HYU/g;
    s/ひょ/HYO/g;
    s/みゃ/MYA/g;
    s/みゅ/MYU/g;
    s/みょ/MYO/g;
    s/りゃ/RYA/g;
    s/りゅ/RYU/g;
    s/りょ/RYO/g;
    s/ぎゃ/GYA/g;
    s/ぎゅ/GYU/g;
    s/ぎょ/GYO/g;
    s/じゃ/JA/g;
    s/じゅ/JU/g;
    s/じょ/JO/g;
    s/びゃ/BYA/g;
    s/びゅ/BYU/g;
    s/びょ/BYO/g;
    s/ぴゃ/PYA/g;
    s/ぴゅ/PYU/g;
    s/ぴょ/PYO/g;

# ヘボン式では b, m, p の前にn の代わりに m をおく

    s/NB/MB/g;
    s/NM/MM/g;
    s/NP/MP/g;

# 促音は子音を重ねて示す

    s/っ(\w)/$1$1/g;

# 長音表記 'おお'，'おう'を Oと表現

    s/OO/O/g;
    s/OU/O/g;

    return $_;
}

sub print_index(){
  print <<"_HTML_";
<!DOCTYPE html>
<html class="no-js">
  <head>
    <meta charset='utf-8' />
    <title>Developers Convention - $title</title>
    <script src="naming.js" type="text/javascript"></script>
  </head>
  <body style="margin: 0; padding: 0;" onLoad="naming('q', 'r')">
  <div id="site_bar" style="margin: 0px auto; background: #E00; color: #FFF;padding: 2px 15px 2px 15px;">
    <center>
    <a href="/dc"><img src="../img/DevelopersConvention.png" /></a>
    </center>
    <a href="/dc/naming" style="color: #FFF;">Naming</a>
    &nbsp;
    <a href="/dc/as" style="color: #FFF;">Association Search</a>
    &nbsp;
    <a href="/dc/cs" style="color: #FFF;">Code Snippet</a>
    &nbsp;
    <a href="/dc/db" style="color: #FFF;">DB</a>
    &nbsp;
    <a href="/dc/wiki" style="color: #FFF;">Wiki</a>
  </div>

  <div align="center" class="naming_form">
    <div class="naming_title">
      <h2>
        <img src="/favicon.ico" width="40" height="40" />
        $title
      </h2>
    </div>
    <div class="naming_form">
      Japanese Name<textarea id="q" cols="30" rows="5" onKeyPress="enter()">
世界平和年月日
宮里忍</textarea>
      Dictionary<textarea id="dictionary" cols="30" rows="5" onKeyPress="enter()">
年月=ym
年月日=ymd
宮里忍=author</textarea>
      <br />
      <input type="button" value="setter mode" onClick="setter(); naming('q', 'r');"/>
      <input type="button" value="getter mode" onClick="getter(); naming('q', 'r');"/>
      <input type="button" value="reset options" onClick="reset_option(); naming('q', 'r');">
      <br />
      <hr />
      Prefix : <input type="text" size="3" name="prefix" id="prefix" value="" onChange="naming('q', 'r')"/>
      Suffix : <input type="text" size="3" name="suffix" id="suffix" value="" onChange="naming('q', 'r')"/>
      Separate : <input type="text" size="1" name="separate" id="separate" value="_" onChange="naming('q', 'r')"/>
      <br />
      Style : 
      <input type="radio" name="naming_style" value="hepburn" id="hepburn" onChange="naming('q', 'r')" checked>Hepburn
      <input type="radio" name="naming_style" value="english" id="english" onChange="naming('q', 'r')">English
      <br />
      Case Sensitivity : 
      <input type="radio" name="case_ensitivity" value="upper case" id="upper case" onChange="naming('q', 'r')" checked>Uppercase
      <input type="radio" name="case_ensitivity" value="lower case" id="lower case" onChange="naming('q', 'r')">Lowercase
      <input type="radio" name="case_ensitivity" value="upper case first" id="upper case first" onChange="naming('q', 'r')">Uppercase First
      <input type="radio" name="case_ensitivity" value="lower case first" id="lower case first" onChange="naming('q', 'r')">Lowercase First
      <br />
      <input type="checkbox" name="first_letter_always_lowercase" value="1" id="first_letter_always_lowercase" onChange="naming('q', 'r')">First letter be always Lowercase(java friendly)
    </div>
  </div>

  <div id="r">
  </div>

  </body>
</html>
_HTML_
}
