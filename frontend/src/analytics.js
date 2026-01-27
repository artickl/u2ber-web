/**
 * Google Analytics integration
 * Only loads in production when VITE_GA_TAG is set
 */

export const initGA = () => {
  const gaTag = import.meta.env.VITE_GA_TAG
  const environment = import.meta.env.VITE_ENVIRONMENT

  // Only load GA in production and when tag is provided
  if (environment !== 'production' || !gaTag || gaTag.trim() === '') {
    console.log('Google Analytics: Disabled (not in production or no tag set)')
    return false
  }

  // Check if already loaded
  if (window.gtag) {
    console.log('Google Analytics: Already loaded')
    return true
  }

  try {
    // Create and inject gtag.js script
    const script = document.createElement('script')
    script.async = true
    script.src = `https://www.googletagmanager.com/gtag/js?id=${gaTag}`
    document.head.appendChild(script)

    // Initialize dataLayer and gtag function
    window.dataLayer = window.dataLayer || []
    window.gtag = function() {
      window.dataLayer.push(arguments)
    }
    
    window.gtag('js', new Date())
    window.gtag('config', gaTag)

    console.log(`Google Analytics: Loaded with tag ${gaTag}`)
    return true
  } catch (error) {
    console.error('Google Analytics: Failed to load', error)
    return false
  }
}

/**
 * Track page view
 */
export const trackPageView = (url) => {
  if (window.gtag && import.meta.env.VITE_ENVIRONMENT === 'production') {
    window.gtag('config', import.meta.env.VITE_GA_TAG, {
      page_path: url,
    })
  }
}

/**
 * Track custom event
 */
export const trackEvent = (action, category, label, value) => {
  if (window.gtag && import.meta.env.VITE_ENVIRONMENT === 'production') {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value,
    })
  }
}
