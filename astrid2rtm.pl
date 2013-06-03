#!/usr/bin/env perl

use strict;
use warnings;
use Moo;
use MooX::Types::MooseLike::Base qw( ArrayRef );
use XML::Simple;
use Time::Stamp 'localstamp';
# TODO: use Getopt::Long qw( GetOptions );

has xml_parser => (
  is      => 'lazy',
  builder => 1,
);

has default_tags => (
  is      => 'ro',
  isa     => ArrayRef,
  default => sub { ['astrid'] },
);

sub _build_xml_parser {
  XML::Simple->new(
    ForceArray => [qw(
      task
      metadata
    )],
    KeyAttr => [],
  );
}

sub parse_xml {
  my ($self, $xml) = @_;
  $self->xml_parser->xml_in($xml);
}

sub run {
  my ($self, $in) = @_;
  my $astrid = $self->parse_xml($in);

  die 'Only known to work with dump format == 2'
    if $astrid->{format} != 2;

  #use YAML::Any; print YAML::Any::Dump($astrid->{task});
  print sort map { $self->smart_add($_) } @{ $astrid->{task} };

}

sub format_due_date {
  my ($self, $date) = @_;
  return unless $date;
  $date =~ s/000$//
    or die "Date '$date' in unknown format";
  return localstamp($date);
}

sub priority {
  my ($self, $priority) = @_;
  # off by one error ;-)
  return $priority + 1;
}

my %freq = (
  DAILY   => 'days',
  MONTHLY => 'months',
  WEEKLY  => 'weeks',
  YEARLY  => 'years',
);
my %day  = (
  SU => 'Sunday',
);

sub format_repeat {
  my ($self, $repeat) = @_;
  return unless $repeat;

  die 'Unknown recurrence format'
    unless $repeat =~ s/^RRULE:((?:[A-Z]+=[^;]+;?)+)$/$1/;

  my %attr = map { split /=/ } split /;/, $repeat;

  return join(' ', grep { $_ }
    (
      $attr{INTERVAL}
        ? ( every => $attr{INTERVAL}, $freq{ $attr{FREQ} } )
        : lc($attr{FREQ})
    ),
    ($attr{BYDAY} ? (on => $day{ $attr{BYDAY} } || $attr{BYDAY}) : ()),
  );
}

sub smart_add {
  my ($self, $task) = @_;
  return join(' ', grep { $_ }
    $task->{title},
    $self->format_tags($task),
    $self->smart_part('!', $self->priority($task->{importance})),
    $self->smart_part('^', $self->format_due_date($task->{dueDate})),
    $self->smart_part('*', $self->format_repeat($task->{recurrence})),
  ) . "\n";
}

sub smart_part {
  my ($self, $prefix, $value) = @_;
  return $value ? $prefix . $value : '';
}

sub format_tags {
  my ($self, $task) = @_;

  my $tags = [ grep { $_->{key} eq 'tags-tag' } @{ $task->{metadata} || [] } ];
  $tags = [$tags] unless ref($tags) eq 'ARRAY';

  return ( map { '#' . $_ }
    @{ $self->default_tags },

    # tag these so they can easily be found and fixed in the web interface
    ($task->{completed} ? 'astrid-completed' : ()),
    ($task->{notes}     ? 'astrid-notes'     : ()),

    map { $_->{value} } @$tags,
  );
}

__PACKAGE__->new->run(@ARGV);
