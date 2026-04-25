export const languages = {
  SO: 'so',
  EN: 'en',
} as const

export type AppLanguage = (typeof languages)[keyof typeof languages]

export const defaultLang: AppLanguage = languages.SO
export const languageStorageKey = 'warka_lang'

export function isLanguage(value: string | null | undefined): value is AppLanguage {
  return value === languages.SO || value === languages.EN
}

export function getStoredLanguage(): AppLanguage {
  if (typeof window === 'undefined') {
    return defaultLang
  }

  const storedLanguage = window.localStorage.getItem(languageStorageKey)
  return isLanguage(storedLanguage) ? storedLanguage : defaultLang
}

export function setStoredLanguage(lang: AppLanguage) {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.setItem(languageStorageKey, lang)
  window.dispatchEvent(new Event('languagechange'))
}

export const ui = {
  en: {
    accessibility: {
      skipToContent: 'Skip to content',
      toggleNavigation: 'Toggle navigation',
      switchToSomali: 'Switch interface language to Somali',
      switchToEnglish: 'Switch interface language to English',
      storyLanguage: 'Story language',
    },
    brand: {
      name: 'Warka',
      report: 'Somali and global report',
      transparency: 'Source transparency and comparison',
      edition: 'Reader edition',
      description:
        'Independent Somali news with source transparency, clearer comparison, and a calmer way to follow what matters.',
    },
    nav: {
      home: 'Home',
      latest: 'Latest',
      somalia: 'Somalia',
      world: 'World',
      compare: 'Compare',
      about: 'About',
    },
    languages: {
      so: 'Soomaali',
      en: 'English',
      shortSo: 'SO',
      shortEn: 'EN',
    },
    home: {
      eyebrow: 'Warka front page',
      headline: 'A calmer way to follow Somalia and the world around it.',
      deck:
        'The interface follows your language preference while reporting stays in its original voice, so readers can move between Somali and English without confusion.',
      quickBriefTitle: 'Morning brief',
      quickBriefSummary: 'Three developments setting the agenda right now.',
    },
    briefing: {
      kicker: 'Today in Warka',
      title: 'Understand the day in ten seconds.',
      deck:
        'A compact briefing on what matters, what is being compared, and which sources are active now.',
      importantStories: 'key stories',
      comparedIssues: 'issues under comparison',
      breakingStories: 'breaking signals',
      verifiedSources: 'verified sources',
    },
    sections: {
      topStories: 'Top Stories',
      topStoriesSubtitle: 'The strongest reporting at the center of today’s conversation.',
      latestStories: 'Latest Stories',
      latestStoriesSubtitle: 'Fresh reporting from active Somali and international sources.',
      compareCoverage: 'Compare Coverage',
      compareCoverageSubtitle:
        'Read the same story through more than one newsroom and see where the angles diverge.',
      somalia: 'Somalia',
      somaliaSubtitle: 'Politics, security, economy, and public life from across the country.',
      world: 'World',
      worldSubtitle: 'International developments with direct relevance to Somali readers.',
    },
    pages: {
      latest: {
        title: 'Latest Stories',
        subtitle: 'The newest reporting from Warka’s source network, arranged in a calm rolling feed.',
        loadErrorTitle: 'We could not load the latest stories',
        loadErrorMessage: 'The latest feed is temporarily unavailable. Please try again shortly.',
        emptyTitle: 'No stories yet',
        emptyMessage: 'Ingestion may still be running.',
      },
      somalia: {
        title: 'Somalia',
        subtitle:
          'Essential reporting from across the country, gathered with the same editorial clarity as the front page.',
      },
      world: {
        title: 'World',
        subtitle: 'Global reporting that helps Somali readers keep the wider picture in view.',
      },
      compare: {
        title: 'Compare Coverage',
        subtitle:
          'See how different outlets cover the same story, what they agree on, and where their emphasis shifts.',
        emptyTitle: 'No comparisons yet',
        emptyMessage: 'Clusters will appear here once stories are ingested and grouped.',
      },
      about: {
        title: 'About Warka',
        lead:
          'Warka is an independent news product built to make Somali and international reporting easier to follow without flattening sources into one voice.',
        missionTitle: 'Our mission',
        missionBody:
          'We believe better-informed readers come from seeing clear attribution, original headlines, and multiple perspectives presented without clutter.',
        somaliaTitle: 'Somalia-first coverage',
        somaliaBody:
          'Warka keeps Somalia at the center while still following the wider world closely, especially when international developments shape Somali civic, economic, or diaspora life.',
        transparencyTitle: 'Source transparency',
        transparencyBody:
          'Every story stays tied to its original publisher so readers can move directly from our brief to the source material and judge the reporting for themselves.',
        compareTitle: 'Compare coverage',
        compareBody:
          'Our comparison workflow highlights where stories converge, where they diverge, and how tone or emphasis changes across outlets in Somali and English.',
        independenceTitle: 'Editorial independence',
        independenceBody:
          'Warka does not sell coverage or hide attribution. Selection is guided by relevance, credibility, and reader usefulness.',
      },
      story: {
        summaryTitle: 'Summary',
        readOriginalPrefix: 'Read the original story on',
        notFound: 'Story not found',
      },
    },
    cards: {
      leadStory: 'Lead story',
      sourceLabel: 'Source',
      languageLabel: 'Language',
      noImage: 'No image',
      readMore: 'Read more',
    },
    compare: {
      kicker: 'Signature feature',
      reportLabel: 'Coverage lens',
      agreement: 'What both reports establish',
      differences: 'Where the framing shifts',
      sources: 'Sources',
      sourceCount: 'Sources',
      languageMix: 'Language mix',
      storyCount: 'Stories',
      trustTitle: 'Source signals',
      verdict: 'Editorial summary',
      hideStories: 'Hide stories',
      viewStories: 'View stories',
      developing: 'This story is still developing across the reporting set.',
      noCoverageTitle: 'Compare coverage is warming up',
      noCoverageMessage: 'A multi-source comparison will appear here as matching stories arrive.',
    },
    storyTrust: {
      keyPoints: 'What to know',
      sourceRailTitle: 'Source transparency',
      source: 'Source',
      language: 'Language',
      reportType: 'Report type',
      sourcePrefix: 'Reported by',
      wireOrInternational: 'International or wire report',
      originalOrLocal: 'Somali or original source',
      published: 'Published',
    },
    states: {
      frontPageUnavailableTitle: 'We could not load the front page just now',
      frontPageUnavailableMessage:
        'The latest stories are temporarily unavailable. Please try again in a moment.',
      genericEmptyTitle: 'No stories found',
      genericEmptyMessage: 'Check back later for updates.',
      noSomaliaTitle: 'No Somalia stories yet',
      noSomaliaMessage: 'Check back as new reporting arrives from the country.',
      noWorldTitle: 'No world stories yet',
      noWorldMessage: 'International coverage will appear here as feeds update.',
    },
    footer: {
      sectionsHeading: 'Sections',
      aboutHeading: 'About',
      methodology: 'Methodology',
      transparency: 'Source transparency',
      rightsReserved: 'All rights reserved.',
    },
    meta: {
      ago: 'ago',
      readTimeSuffix: 'min read',
      seconds: 'second',
      secondsPlural: 'seconds',
      minutes: 'minute',
      minutesPlural: 'minutes',
      hours: 'hour',
      hoursPlural: 'hours',
      days: 'day',
      daysPlural: 'days',
      weeks: 'week',
      weeksPlural: 'weeks',
      months: 'month',
      monthsPlural: 'months',
    },
  },
  so: {
    accessibility: {
      skipToContent: 'U gudub nuxurka',
      toggleNavigation: 'Fur ama xir hagaha',
      switchToSomali: 'U beddel luqadda muuqaalka Soomaali',
      switchToEnglish: 'U beddel luqadda muuqaalka English',
      storyLanguage: 'Luqadda sheekada',
    },
    brand: {
      name: 'Warka',
      report: 'Warbixin Soomaali iyo caalami ah',
      transparency: 'Hufnaan ilo iyo isbarbardhig daboolid',
      edition: 'Nooca akhristaha',
      description:
        'Warar madaxbannaan oo Soomaali ah, leh hufnaan ilo, isbarbardhig cad, iyo qaab deggan oo lagu fahmo waxa muhiimka ah.',
    },
    nav: {
      home: 'Bogga Hore',
      latest: 'Ku Cusub',
      somalia: 'Soomaaliya',
      world: 'Caalamka',
      compare: 'Isbarbardhig',
      about: 'Ku Saabsan',
    },
    languages: {
      so: 'Soomaali',
      en: 'English',
      shortSo: 'SO',
      shortEn: 'EN',
    },
    home: {
      eyebrow: 'Bogga hore ee Warka',
      headline: 'Qaab deggan oo lagula socdo Soomaaliya iyo dunida ku xeeran.',
      deck:
        'Muuqaalku waxa uu raacayaa luqadda aad doorato, halka warbixintu ku sii jirto codkeedii asalka ahaa, si akhrisku uga dhex socdo Soomaali iyo English si cad.',
      quickBriefTitle: 'War-kooban subaxeed',
      quickBriefSummary: 'Saddex qodob oo dejinaya ajandaha maanta.',
    },
    briefing: {
      kicker: 'Maanta Warka',
      title: 'Ku faham maalinta toban ilbiriqsi.',
      deck:
        'War-kooban oo muujinaya waxa muhiimka ah, waxa la isbarbar dhigayo, iyo ilaha hadda firfircoon.',
      importantStories: 'sheeko muhiim ah',
      comparedIssues: 'arrimo la isbarbar dhigayo',
      breakingStories: 'calaamado degdeg ah',
      verifiedSources: 'ilo la xaqiijiyay',
    },
    sections: {
      topStories: 'Sheekooyinka Ugu Muhiimsan',
      topStoriesSubtitle: 'Warbixinta ugu xooggan ee ku jirta xudunta wada hadalka maanta.',
      latestStories: 'Kuwa Ugu Danbeeyay',
      latestStoriesSubtitle: 'Warar cusub oo ka imanaya ilo Soomaali iyo caalami ah oo firfircoon.',
      compareCoverage: 'Isbarbardhig Daboolid',
      compareCoverageSubtitle:
        'Akhri sheeko isku mid ah oo ay wargeysyo kala duwan ka warrameen, kana arag halka xagalladu isku beddelayaan.',
      somalia: 'Soomaaliya',
      somaliaSubtitle: 'Siyaasad, amni, dhaqaale, iyo nolol bulsho oo dalka oo dhan laga soo tebiyey.',
      world: 'Caalamka',
      worldSubtitle: 'Horumarro caalami ah oo saamayn toos ah ku leh akhristaha Soomaaliyeed.',
    },
    pages: {
      latest: {
        title: 'Kuwa Ugu Danbeeyay',
        subtitle:
          'Warbixintii ugu cuslayd ee ilaha Warka laga helay, loona habeeyey si deggan oo sahlan in la raaco.',
        loadErrorTitle: 'Ma aanan soo qaadi karin wararkii ugu dambeeyay',
        loadErrorMessage: 'Qulqulka wararka hadda si ku meel gaar ah looma heli karo. Mar kale isku day waxyar kadib.',
        emptyTitle: 'Weli ma jiraan sheekooyin',
        emptyMessage: 'Waxaa dhici karta in gelinta xogtu wali socoto.',
      },
      somalia: {
        title: 'Soomaaliya',
        subtitle:
          'Warbixinta muhiimka ah ee dalka oo dhan laga helay, isla caddayntii tafatireed ee bogga hore leh.',
      },
      world: {
        title: 'Caalamka',
        subtitle: 'Wararka caalamka ee ka caawinaya akhristaha Soomaaliyeed inuu arko sawirka ballaaran.',
      },
      compare: {
        title: 'Isbarbardhig Daboolid',
        subtitle:
          'Arag sida warbaahin kala duwan uga hadlaan hal sheeko, waxa ay isku raacsan yihiin, iyo halka xoogga uu isu beddelo.',
        emptyTitle: 'Weli ma jiraan isbarbardhigyo',
        emptyMessage: 'Kooxo isku mawduuc ah ayaa halkan kasoo muuqan doona marka sheekooyinka la ururiyo oo la isu geeyo.',
      },
      about: {
        title: 'Ku Saabsan Warka',
        lead:
          'Warka waa madal war oo madax-bannaan oo loogu talagalay in akhriska wararka Soomaalida iyo kuwa caalamkaba laga dhigo mid fudud, cad, oo aan lumin codka ilaha.',
        missionTitle: 'Himiladeenna',
        missionBody:
          'Waxaan rumaysanahay in akhriste xog-ogaal ahi ka dhasho marka la helo xigasho cad, cinwaanno asal ah, iyo aragtiyo kala duwan oo aan buuq lahayn.',
        somaliaTitle: 'Daboolid Soomaaliya salka ku haysa',
        somaliaBody:
          'Warka waxay Soomaaliya ka dhigtaa bartamaha, iyadoo haddana si dhow ula socota dunida inteeda kale, gaar ahaan marka arrimaha caalamku saameeyaan nolosha bulshada Soomaaliyeed.',
        transparencyTitle: 'Hufnaanta ilaha',
        transparencyBody:
          'Sheeko kasta waxa ay ku xiran tahay daabacaddii asalka ahayd si akhristuhu uga gudbi karo war-koobkayaga una gaadhi karo warbixinta asalka ah.',
        compareTitle: 'Isbarbardhig daboolid',
        compareBody:
          'Habkayaga isbarbardhiggu waxa uu muujinayaa halka sheekooyinku ku kulmaan, halka ay ku kala leexdaan, iyo sida codka ama xooggu isugu beddelo warbaahinta Soomaaliyeed iyo tan English-ka.',
        independenceTitle: 'Madaxbannaanida tafatirka',
        independenceBody:
          'Warka ma iibiso daboolid mana qarisid ilaha. Doorashadu waxa hagaya muhiimad, sumcad, iyo waxtarka akhristaha.',
      },
      story: {
        summaryTitle: 'Soo koobid',
        readOriginalPrefix: 'Ka akhri sheekada asalka ah',
        notFound: 'Sheekada lama helin',
      },
    },
    cards: {
      leadStory: 'Sheekada hormuudka ah',
      sourceLabel: 'Isha',
      languageLabel: 'Luqad',
      noImage: 'Sawir ma jiro',
      readMore: 'Akhriso',
    },
    compare: {
      kicker: 'Astaanta gaarka ah',
      reportLabel: 'Muraayadda daboolidda',
      agreement: 'Waxa labada warbixin isla xaqiijinayaan',
      differences: 'Halka qaabayntu ka leexato',
      sources: 'Ilaha',
      sourceCount: 'Ilaha',
      languageMix: 'Luqadaha',
      storyCount: 'Sheekooyin',
      trustTitle: 'Calaamadaha ilaha',
      verdict: 'Soo koobid tafatireed',
      hideStories: 'Qari sheekooyinka',
      viewStories: 'Muuji sheekooyinka',
      developing: 'Sheekadan weli si kala duwan ayaa looga sii warramayaa.',
      noCoverageTitle: 'Qaybta isbarbardhiggu way soo diyaaraysaa',
      noCoverageMessage: 'Isbarbardhig ilo badan leh ayaa halkan kasoo muuqan doona marka sheekooyin is-waafaqsan soo galaan.',
    },
    storyTrust: {
      keyPoints: 'Waxa muhiimka ah',
      sourceRailTitle: 'Hufnaanta ilaha',
      source: 'Isha',
      language: 'Luqadda',
      reportType: 'Nooca warbixinta',
      sourcePrefix: 'Waxaa qoray',
      wireOrInternational: 'Warbixin caalami ah ama wire',
      originalOrLocal: 'Ilo Soomaali ama asal ah',
      published: 'La daabacay',
    },
    states: {
      frontPageUnavailableTitle: 'Ma aanan soo qaadi karin bogga hore hadda',
      frontPageUnavailableMessage:
        'Wararkii ugu dambeeyay si ku meel gaar ah looma heli karo. Fadlan mar kale isku day daqiiqado kadib.',
      genericEmptyTitle: 'Wax sheekooyin ah lama helin',
      genericEmptyMessage: 'Dib u soo laabo mar dambe si aad u hesho warar cusub.',
      noSomaliaTitle: 'Weli ma jiraan warar Soomaaliya ah',
      noSomaliaMessage: 'Dib u eeg marka warbixin cusub dalka kasoo gaadho.',
      noWorldTitle: 'Weli ma jiraan warar caalami ah',
      noWorldMessage: 'Wararka caalamka ayaa halkan kasoo muuqan doona marka iluhu cusboonaadaan.',
    },
    footer: {
      sectionsHeading: 'Qaybaha',
      aboutHeading: 'Faahfaahin',
      methodology: 'Habraaca',
      transparency: 'Hufnaanta ilaha',
      rightsReserved: 'Xuquuqda oo dhan way dhowran tahay.',
    },
    meta: {
      ago: 'kahor',
      readTimeSuffix: 'daqiiqo akhris',
      seconds: 'ilbiriqsi',
      secondsPlural: 'ilbiriqsi',
      minutes: 'daqiiqo',
      minutesPlural: 'daqiiqo',
      hours: 'saac',
      hoursPlural: 'saacadood',
      days: 'maalin',
      daysPlural: 'maalmo',
      weeks: 'toddobaad',
      weeksPlural: 'toddobaadyo',
      months: 'bil',
      monthsPlural: 'bilo',
    },
  },
} as const

export type UIStrings = (typeof ui)[AppLanguage]

export function getDictionary(lang: AppLanguage) {
  return ui[lang]
}

export function formatReadTime(minutes: number, lang: AppLanguage) {
  return `${minutes} ${ui[lang].meta.readTimeSuffix}`
}

function getRelativeUnit(value: number, singular: string, plural: string) {
  return Math.abs(value) === 1 ? singular : plural
}

export function formatRelativeTime(date: string, lang: AppLanguage) {
  const elapsedMs = Date.now() - new Date(date).getTime()
  const elapsedSeconds = Math.max(1, Math.round(elapsedMs / 1000))
  const dictionary = ui[lang].meta

  const ranges = [
    { limit: 60, value: elapsedSeconds, singular: dictionary.seconds, plural: dictionary.secondsPlural },
    {
      limit: 60 * 60,
      value: Math.round(elapsedSeconds / 60),
      singular: dictionary.minutes,
      plural: dictionary.minutesPlural,
    },
    {
      limit: 60 * 60 * 24,
      value: Math.round(elapsedSeconds / (60 * 60)),
      singular: dictionary.hours,
      plural: dictionary.hoursPlural,
    },
    {
      limit: 60 * 60 * 24 * 7,
      value: Math.round(elapsedSeconds / (60 * 60 * 24)),
      singular: dictionary.days,
      plural: dictionary.daysPlural,
    },
    {
      limit: 60 * 60 * 24 * 30,
      value: Math.round(elapsedSeconds / (60 * 60 * 24 * 7)),
      singular: dictionary.weeks,
      plural: dictionary.weeksPlural,
    },
    {
      limit: Number.POSITIVE_INFINITY,
      value: Math.round(elapsedSeconds / (60 * 60 * 24 * 30)),
      singular: dictionary.months,
      plural: dictionary.monthsPlural,
    },
  ]

  const selectedRange = ranges.find((range) => elapsedSeconds < range.limit) || ranges[ranges.length - 1]
  const label = getRelativeUnit(selectedRange.value, selectedRange.singular, selectedRange.plural)
  return `${selectedRange.value} ${label} ${dictionary.ago}`
}
