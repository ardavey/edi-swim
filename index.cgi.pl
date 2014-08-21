#!/usr/bin/perl
use strict;
use warnings;

use 5.010;

use WWW::Mechanize;
use HTML::TreeBuilder;
use Time::HiRes qw( gettimeofday tv_interval );

use CGI qw( std );
use CGI::Ajax;

my $start = [ gettimeofday() ];
my $q = CGI->new();
my $ajx = CGI::Ajax->new( 'get_programme_url' => \&get_programme_url );

say $ajx->build_html( $q, \&get_html );

sub get_html {
  my $venues = get_venues();
  my $ret = start_page( $q, $venues );
  $ret .= print_venues( $q, $venues );
  my $time = tv_interval( $start, [ gettimeofday() ] );
  $ret .= end_page( $q, $time );
  return $ret;
}

sub start_page {
  my ( $q, $venues ) = @_;
  my @ids = ();
  foreach my $venue ( @$venues ) {
    push @ids, $venue->{id};
  }
  my $id_string = join( "','", @ids );
  my $title = 'Edinburgh Leisure Pool Programmes';
  my $ret = $q->start_html( { style => 'style.css',
                              title => $title } )
            . $q->h2( $title )
            . $q->p( 'Here is a list of all Edinburgh Leisure swimming pools with links to their info page.' )
            . $q->p( 'Links with an icon next to them will load the relevant timetable instead.' );
  return $ret;
}

sub get_venues {
  my ( $q ) = @_;
  my $base_url = 'http://www.edinburghleisure.co.uk';
  
  my $mech = WWW::Mechanize->new();
  $mech->get( $base_url . '/venues' );
  
  my $tree = HTML::TreeBuilder->new();
  $tree->parse_content( $mech->content );
  
  my @detail_divs = $tree->look_down(
    _tag => 'div',
    class => 'details',
    sub { $_[0]->as_text() =~ m/swimming/i },
  );

  my @venues = ();
  foreach my $div ( @detail_divs ) {
    my @venuenames = $div->look_down( _tag => 'h2' );
    my $venuename = $venuenames[0]->as_text();

    ( my $id = $venuename ) =~ s!\s+!-!g;
    $id =~ s!^(.*)$!\L$1!g;

    my $links_ref = $div->extract_links( 'a' );
    my $link = $base_url . $links_ref->[0]->[0];
    
    push @venues, {
      name => $venuename,
      id => $id,
      url => $link,
    };
  }
  
  return \@venues;
}

sub print_venues {
  my ( $q, $venues ) = @_;
  
  my $ret = '';
  $ret .= $q->start_ul();
  
  foreach my $venue ( @$venues ) {
    $ret .= $q->li( $q->div( { id => $venue->{id} },
                             $q->img( { src => 'swim.gif',
                               width => 16,
                               height => 16,
                               style => "visibility:hidden",
                               onload => "get_programme_url( ['$venue->{id}'], ['$venue->{id}'] )"
                              } ),
                             $q->a( { href => $venue->{url} },
                                    $venue->{name}
                                  )
                            ) );
  }

  $ret .= $q->end_ul();
  
  return $ret;
}

sub end_page {
  my ( $q, $time ) = @_;
  
  my $ret = $q->p( $q->small( "Completed in $time seconds." ) )
            . $q->end_html();
  return $ret;
}

sub get_programme_url {
  my ( $html_link ) = @_;
  my $mech = WWW::Mechanize->new();

  my ( $url ) = $html_link =~ m/href="(.*?)"/;
  $mech->get( $url );
  my $prog_url = ( $mech->find_all_links( text_regex => qr/(?:download|click) here/i ) )[-1];
  if ( defined $prog_url ) {
    $url = $prog_url->url();
  }
  $html_link =~ s/^(.*href=").*?(".*)$/$1$url$2/;
  $html_link =~ s/^(.*) onload=".*?"(.*)$/$1$2/;
  $html_link =~ s/^(.*) style=".*?"(.*)$/$1$2/;
  
  return $html_link;
}
